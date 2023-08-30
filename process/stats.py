import datetime
from typing import Type

import discord
import discord.utils
from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.sql import select

from models import database
from module import pubgpy
from module import statsType
from process.request_loop import request_loop
from process.image import ImageProcess
from process.process_base import ProcessBase


class Stats(ProcessBase):
    def __init__(
        self,
        ctx: interaction.ApplicationContext,
        client: interaction.Client,
        factory: sessionmaker,
        player: pubgpy.Player,
        season: str = None,
        fpp: bool = False,
        **kwargs,
    ):
        self.context = ctx
        self.client = client
        self.factory = factory
        self.player = player
        self.season = season
        self.fpp = fpp

        self.matches_class = kwargs.get("matches")
        super().__init__(self.context, self.client, self.factory, self.player)

        self.data: dict[
            Type[database.NormalStats | database.RankedStats],
            dict[statsType.StatsPlayType, database.NormalStats | database.RankedStats],
        ] = {}
        self.image = ImageProcess(player, self.context.locale)

        self.before_func = None
        self.before_type = None

    async def load_favorite(self, session: AsyncSession = None) -> bool:
        result = await super(Stats, self).load_favorite(session)
        if self.matches_class is not None:
            self.matches_class.is_favorite = result
        return result

    async def response_component(
        self,
        component_context: interaction.ComponentsContext | None = None,
        content: str = discord.utils.MISSING,
        embeds: list[discord.Embed] = None,
        attachments: list[discord.File] = discord.utils.MISSING,
        **kwargs,
    ):
        context = await super(Stats, self).response_component(
            component_context, content, embeds, attachments, **kwargs
        )
        if context is None:
            return
        match context.custom_id:
            case self.normal_stats_button.custom_id:
                await self.normal_stats(context)
            case self.ranked_stats_button.custom_id:
                await self.ranked_stats(context)
            case self.matches_stats_button.custom_id:
                matches_id = await self.matches_class.match_selection()
                if matches_id is None:
                    return
                await self.matches_class.match_info(matches_id=matches_id)
            case self.favorite_stats_button.custom_id:
                await self.update_favorite()
                await self.before_func(context)
            case self.update_stats_button.custom_id:
                await self.update_data(self.before_type, update=True)
                await self.before_func(context)
        return

    @staticmethod
    def game_type_from_data_type(
        data_type: Type[database.NormalStats | database.RankedStats],
    ) -> list[statsType.StatsPlayType]:
        return (
            [
                # statsType.StatsPlayType.SOLO,
                statsType.StatsPlayType.SQUAD
            ]
            if data_type == database.RankedStats
            else list(statsType.StatsPlayType)
        )

    async def update_data(
        self,
        data_type: Type[database.NormalStats | database.RankedStats],
        session: AsyncSession = None,
        update: bool = False,
    ):
        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        match data_type:
            case database.NormalStats:
                data: pubgpy.GameModeReceive = await request_loop(
                    self.context, self.player.season_stats, season=self.season
                )
            case database.RankedStats:
                data: pubgpy.GameModeReceive = await request_loop(
                    self.context, self.player.ranked_stats, season=self.season
                )
            case _:
                raise TypeError("Bad Argument")

        if data_type not in self.data:
            self.data[data_type] = {}

        data_type_game_mode = self.game_type_from_data_type(data_type)
        for game_mode in data_type_game_mode:
            _data = getattr(data, game_mode.value + ("_fpp" if self.fpp else ""))
            self.data[data_type][game_mode] = _formatted_data = data_type.from_pubg(
                player=self.player.id,
                season=self.season,
                stats=_data,
                play_type=game_mode,
                fpp=self.fpp,
                update_time=datetime.datetime.now()
            )

            if not update:
                session.add(_formatted_data)
            else:
                await session.merge(_formatted_data)

        await session.commit()
        if only_session:
            await session.close()
        return self.data

    async def load_data(
        self,
        data_type: Type[database.NormalStats | database.RankedStats],
        session: AsyncSession = None,
    ) -> dict[
        statsType.StatsPlayType, database.NormalStats | database.RankedStats
    ] | None:
        if (
            data_type in self.data.keys()
            and self.game_type_from_data_type(data_type)
            == self.data.get(data_type, {}).keys()
        ):
            return self.data[data_type]

        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        query = select(
            # exists(data_type).where(data_type.account_id_with_session == f"{self.player.id}_{self.season.id}_solo")
            exists(data_type).where(
                (data_type.account_id == self.player.id)
                & (data_type.season == self.season)
            )
        )
        data: AsyncResult = await session.execute(query)
        if data.scalar_one_or_none():
            data_type_game_mode = self.game_type_from_data_type(data_type)
            if data_type not in self.data:
                self.data[data_type] = {}
            for game_mode in data_type_game_mode:
                query = select(data_type).where(
                    (data_type.account_id == self.player.id)
                    & (data_type.season == self.season)
                    & (data_type.type == game_mode)
                )
                _data: data_type = await session.scalar(query)
                self.data[data_type][game_mode] = _data
        else:
            await self.update_data(data_type, session)

        if only_session:
            await session.close()
        return self.data[data_type]

    async def ranked_stats(
        self, component_response: interaction.ComponentsContext | None = None
    ):
        if database.RankedStats not in self.data.keys():
            await self.load_data(database.RankedStats)
        self.before_func = self.ranked_stats
        self.before_type = database.RankedStats
        self.init_button()
        data = self.data[database.RankedStats]
        image = self.image.ranked_stats(data)
        file = discord.File(
            image, filename="{}_ranked_stats.png".format(self.player.name)
        )
        self.ranked_stats_button.style = 3
        self.ranked_stats_button.disabled = True
        await self.response_component(component_response, attachments=[file])
        return

    async def normal_stats(
        self, component_response: interaction.ComponentsContext | None = None
    ):
        if database.NormalStats not in self.data.keys():
            await self.load_data(database.NormalStats)
        self.before_func = self.normal_stats
        self.before_type = database.NormalStats
        self.init_button()
        data = self.data[database.NormalStats]
        image = self.image.normal_stats(data)
        file = discord.File(
            image, filename="{}_noraml_stats.png".format(self.player.name)
        )
        self.normal_stats_button.style = 3
        self.normal_stats_button.disabled = True
        await self.response_component(component_response, attachments=[file])
        return
