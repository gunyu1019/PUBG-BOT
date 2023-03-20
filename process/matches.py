import asyncio
import datetime
import aiohttp
import discord
from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import delete
from sqlalchemy.sql import select

from config.config import get_config
from models import database
from module import pubgpy
from process.process_base import ProcessBase
from process.image import ImageProcess
from process.map_assets import MapAssets
from utils.location import comment

parser = get_config()


class MatchesProcess(ProcessBase):
    def __init__(
            self,
            ctx: interaction.ApplicationContext,
            client: interaction.Client,
            factory: sessionmaker,
            player: pubgpy.Player,
            **kwargs
    ):
        self.context = ctx
        self.client = client
        self.factory = factory
        self.player = player

        self.asset_data = None
        self.image = ImageProcess(player, self.context.locale)

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.stats_class = kwargs.get('stats')

        super().__init__(self.context, self.factory, self.player)
        self._matches_id = None

    @property
    def matches_id(self):
        if self._matches_id is None:
            return self.player.matches
        return self._matches_id

    async def response_component(
            self,
            component_context: interaction.ComponentsContext | None = None,
            content: str = discord.utils.MISSING,
            attachments: list[discord.File] = discord.utils.MISSING,
            **kwargs
    ):
        context = await super(MatchesProcess, self).response_component(
            component_context,
            content,
            attachments,
            **kwargs
        )
        match context.custom_id:
            case self.normal_stats_button.custom_id:
                await self.stats_class.normal_stats()
            case self.ranked_stats_button.custom_id:
                await self.stats_class.ranked_stats()
            case self.favorite_stats_button.custom_id:
                await self.update_favorite()
                await self.match_info(kwargs.get('matches_id'), component_context)

    async def load_favorite(self, session: AsyncSession = None) -> bool:
        result = await super(MatchesProcess, self).load_favorite(session)
        if self.stats_class is not None:
            self.stats_class.is_favorite = result
        return result

    async def load_matches_id(self, session: AsyncSession | None = None):
        if len(self.player.matches) == 0:
            only_session = False
            if session is None:
                only_session = True
                session = self.factory.__call__()

            query = select(database.MatchesPlayer).where(database.MatchesPlayer.account_id == self.player.id)
            result = await session.scalars(query)

            match_data = result.all()
            if len(match_data) == 0:
                match_data = await self.update_matches_id(session)

            if len(match_data) == 0:
                embed = discord.Embed(
                    description=comment("matches_process", "matches_not_found", self.context.locale),
                    color=self.warning_color
                )
                await self.context.edit(embed=embed)
                return

            if only_session:
                await session.close()
            self._matches_id = [x.match_id for x in match_data]
        # else:
        #     self._matches_id = self.player.matches
        return self.matches_id

    async def update_matches_id(self, session: AsyncSession | None = None):
        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        await self.player.update()
        query = delete(database.MatchesPlayer).where(database.MatchesPlayer.account_id == self.player.id)
        await session.execute(query)

        data = [database.MatchesPlayer(**{
            "account_id_with_match_id": "{}_{}".format(self.player.id, match_id),
            "account_id": self.player.id,
            "match_id": match_id,
            "match_index": index,
            "last_update": datetime.datetime.now()
        }) for index, match_id in enumerate(self.player.matches)]
        session.add_all(data)
        await session.commit()

        if only_session:
            await session.close()
        return data

    async def match_selection(self, session: AsyncSession | None = None) -> str | None:
        matches_id = await self.load_matches_id(session)
        if matches_id is None:
            return
        embed = discord.Embed(
            title=comment("matches_process", "title", self.context.locale),
            description=comment("matches_process", "description", self.context.locale),
            color=self.warning_color
        )
        components_options = [
            interaction.Options(
                label="{}번째 매치 히스토리".format(index + 1),
                description=match_id,
                value=match_id
            )
            for index, match_id in enumerate(matches_id[0:23])
        ]

        components_options.append(
            interaction.Options(
                label="업데이트",
                value="update",
                description="전적 정보를 업데이트 합니다.",
                emoji=discord.PartialEmoji(id=868344053262061578, name="update")
            )
        )
        components_options.append(
            interaction.Options(
                label="취소",
                value="cancel",
                description="선택을 취소합니다.",
                emoji=discord.PartialEmoji(name="\U0000274C")
            )
        )
        components = interaction.ActionRow(components=[
            interaction.Selection(
                custom_id="matches_selection",
                options=components_options,
                min_values=1, max_values=1
            )
        ])
        await self.context.edit(embed=embed, components=[components], attachments=[])

        try:
            components_response: interaction.ComponentsContext = await self.client.wait_for_global_component(
                check=lambda component: (
                    component.component_type == interaction.Selection.TYPE and
                    "matches_selection" == component.custom_id and
                    self.context.author.id == component.author.id
                ), timeout=300
            )
            components.components[0].disabled = True
            message = await self.context.edit(embed=embed, components=[components])
            await components_response.defer_update()
        except asyncio.TimeoutError:
            return

        if "update" in components_response.values:
            self._matches_id = await self.update_matches_id()
            return await self.match_selection()
        elif "cancel" in components_response.values:
            embed = discord.Embed(
                title=comment("matches_process", "title", self.context.locale),
                description="~~{}~~\n{}".format(
                    comment("matches_process", "description", self.context.locale),
                    comment("matches_process", "canceled", self.context.locale),
                ),
                color=self.color
            )
            await components_response.edit(embed=embed, components=[components])
            return
        return components_response.values[0]

    async def get_assets(self, data: pubgpy.Matches) -> dict:
        if self.asset_data is not None:
            return self.asset_data
        async with aiohttp.ClientSession() as session:
            async with session.request(method="GET", url=data.asset[0].url) as request:
                self.asset_data = await request.json()
        return self.asset_data

    async def match_info(self, matches_id: str, component_response: interaction.ComponentsContext | None = None):
        data = await self.player.client.matches(matches_id)

        assets_data = await self.get_assets(data)
        map_image = MapAssets(player_id=self.player.id, map_name=data.map, data=assets_data)
        map_image.process(kill=True, revive=True, care_package=True, route=True)
        image = await self.image.matches_stats(data, map_image.file)

        file = discord.File(image, filename="{}_matches_stats.png".format(self.player.name))
        self.matches_stats_button.style = 3
        self.matches_stats_button.disabled = True
        self.update_stats_button.disabled = True
        await self.response_component(component_response, attachments=[file])
        return
