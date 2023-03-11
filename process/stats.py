from typing import Type

import discord
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


class Stats:
    def __init__(
            self,
            ctx: interaction.ApplicationContext,
            client: interaction.Client,
            factory: sessionmaker,
            player: pubgpy.Player,
            season: str,
            fpp: bool = False
    ):
        self.context = ctx
        self.client = client
        self.factory = factory
        self.player = player
        self.season = season
        self.fpp = fpp

        self.data: dict[
            Type[database.NormalStats | database.RankedStats],
            dict[statsType.StatsPlayType, database.NormalStats | database.RankedStats]
        ] = {}
        self.image = ImageProcess(player, self.context.locale)

        self.normal_stats_button = interaction.Button(
            custom_id="normal_stats_button",
            emoji=discord.PartialEmoji(name="\U00000031\U0000FE0F\U000020E3"),
            style=1
        )
        self.ranked_stats_button = interaction.Button(
            custom_id="ranked_stats_button",
            emoji=discord.PartialEmoji(name="\U00000032\U0000FE0F\U000020E3"),
            style=1
        )
        self.matches_stats_button = interaction.Button(
            custom_id="matches_stats_button",
            emoji=discord.PartialEmoji(name="\U00000032\U0000FE0F\U000020E3"),
            style=1
        )
        self.favorite_stats_button = interaction.Button(
            custom_id="favorite_stats_button",
            emoji=discord.PartialEmoji(name="\U00002B50"),
            style=1
        )
        self.cancel_stats_button = interaction.Button(
            custom_id="cancel_stats_button",
            emoji=discord.PartialEmoji(name="\U0000274C"),
            style=1
        )

    @property
    def buttons(self) -> interaction.ActionRow:
        return interaction.ActionRow(components=[
            self.normal_stats_button,
            self.ranked_stats_button,
            self.matches_stats_button,
            self.favorite_stats_button,
            self.cancel_stats_button
        ])

    @staticmethod
    def game_type_from_data_type(
            data_type: Type[database.NormalStats | database.RankedStats]
    ) -> list[statsType.StatsPlayType]:
        return [
            # statsType.StatsPlayType.SOLO,
            statsType.StatsPlayType.SQUAD
        ] if data_type == database.RankedStats else list(statsType.StatsPlayType)

    async def update_data(
            self,
            data_type: Type[database.NormalStats | database.RankedStats],
            session: AsyncSession = None,
            update: bool = False
    ):
        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        match data_type:
            case database.NormalStats:
                data: pubgpy.GameModeReceive = await request_loop(
                    self.context,
                    self.player.season_stats,
                    season=self.season
                )
            case database.RankedStats:
                data: pubgpy.GameModeReceive = await request_loop(
                    self.context,
                    self.player.ranked_stats,
                    season=self.season
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
                fpp=self.fpp
            )

            if not update:
                session.add(_formatted_data)

        await session.commit()
        if only_session:
            await session.close()
        return self.data

    async def load_data(
            self,
            data_type: Type[database.NormalStats | database.RankedStats],
            session: AsyncSession = None
    ) -> dict[statsType.StatsPlayType, database.NormalStats | database.RankedStats] | None:
        if (
                data_type in self.data.keys() and
                self.game_type_from_data_type(data_type) == self.data.get(data_type, {}).keys()
        ):
            return self.data[data_type]

        only_session = False
        if session is None:
            only_session = True
            session = self.factory.__call__()

        query = select(
            # exists(data_type).where(data_type.account_id_with_session == f"{self.player.id}_{self.season.id}_solo")
            exists(data_type).where((data_type.account_id == self.player.id) & (data_type.season == self.season))
        )
        data: AsyncResult = await session.execute(query)
        if data.scalar_one_or_none():
            data_type_game_mode = self.game_type_from_data_type(data_type)
            if data_type not in self.data:
                self.data[data_type] = {}
            for game_mode in data_type_game_mode:

                query = select(data_type).where(
                    (data_type.account_id == self.player.id) &
                    (data_type.season == self.season) &
                    (data_type.type == game_mode)
                )
                _data: data_type = await session.scalar(query)
                self.data[data_type][game_mode] = _data
        else:
            await self.update_data(data_type, session)

        if only_session:
            await session.close()
        return self.data[data_type]

    async def ranked_stats(self, component_response: interaction.ComponentsContext | None = None):
        if database.RankedStats not in self.data.keys():
            await self.load_data(database.RankedStats)
        data = self.data[database.RankedStats]
        image = self.image.ranked_stats(data)
        file = discord.File(image, filename="{}_normal_stats.png".format(self.player.name))
        if component_response is None:
            await self.context.edit(attachments=[file])
        return

    async def normal_stats(self, component_response: interaction.ComponentsContext | None = None):
        if database.NormalStats not in self.data.keys():
            await self.load_data(database.NormalStats)
        data = self.data[database.NormalStats]
        image = self.image.normal_stats(data)
        file = discord.File(image, filename="{}_normal_stats.png".format(self.player.name))
        if component_response is None:
            await self.context.edit(attachments=[file])
        return
