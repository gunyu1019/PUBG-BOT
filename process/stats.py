from typing import Type

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

    @staticmethod
    def game_type_from_data_type(
            data_type: Type[database.NormalStats | database.RankedStats]
    ) -> list[statsType.StatsPlayType]:
        return [
            # statsType.StatsPlayType.SOLO,
            statsType.StatsPlayType.SQUAD
        ] if isinstance(data_type, database.RankedStats) else list(statsType.StatsPlayType)

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
                    self.player.season_stats,
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
        if data.one_or_none():
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

    async def ranked_stats(self):
        return

    async def normal_stats(self):
        return
