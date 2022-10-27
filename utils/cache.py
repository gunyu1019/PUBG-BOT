"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""
import asyncio
import pymysql
import pymysql.converters
import aiomysql
import json
import inspect
from datetime import datetime
from pytz import timezone
from typing import Union, Type, Optional, List, Callable

from config.config import parser
from module.database import Database
from utils.database import get_database
from module.pubgpy import player, Client, Season, GameModeReceive, Matches, TooManyRequests


class CacheData:
    def __init__(self, client: Client):
        self.database: Optional[Database] = None
        self.pubg = client

    async def get_database(self):
        self.database = await get_database()

    @staticmethod
    def time() -> datetime:
        return datetime.now(tz=timezone('Asia/Seoul')).replace(tzinfo=None)

    @staticmethod
    def _get_last_update(cls) -> Optional[str]:
        if cls == player.SeasonStats:
            return "season_date"
        elif cls == player.RankedStats:
            return "ranked_date"
        elif cls == player.Player:
            return "matches_date"

    @staticmethod
    def _get_mode(cls) -> Optional[str]:
        if cls == player.SeasonStats:
            return parser.get("DatabaseName", "SeasonStats")
        elif cls == player.RankedStats:
            return parser.get("DatabaseName", "RankedStats")
        elif cls == Matches:
            return parser.get("DatabaseName", "Matches")

    def commit(self):
        return self.database.commit()

    def close(self):
        return self.database.close(check_commit=True)

    @staticmethod
    def _dump_dict(data: Union[dict, list]) -> str:
        return json.dumps(data, indent=4)

    @staticmethod
    def _load_dict(data: Optional[str]) -> Union[dict, list]:
        if data is None:
            return {}
        return json.loads(data)

    async def save_lastupdate(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats, player.Player]],
            dt: datetime
    ):
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        await self.database.update(
            table="player_data",
            key_name="player_id",
            key=player_id,
            value={
                self._get_last_update(cls): dt.strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        await self.commit()
        return

    async def get_lastupdate(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats, player.Player]]
    ) -> Optional[datetime]:
        if self.database is None:
            await self.get_database()
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        data = await self.database.query(
            table="player_data",
            key_name="player_id",
            key=player_id,
            filter_col=[self._get_last_update(cls)]
        )
        result = data.get(self._get_last_update(cls)) if data is not None else None
        return result


class CachePlayData(CacheData):
    def __init__(self, client: Client, too_much_callback: Optional[Callable] = None):
        super().__init__(client)
        self.too_much_callback = too_much_callback

    async def save_play_data(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            data: player.GameModeReceive,
            update: bool = False
    ):
        season = season.id if isinstance(season, Season) else season
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cls = data.type_class
        cur = await self.database.get_cursor(aiomysql.cursors.DictCursor)
        if update:
            command = pymysql.converters.escape_string(
                "UPDATE {} SET player_data=%s WHERE player_id=%s and season = %s".format(self._get_mode(cls))
            )
        else:
            command = pymysql.converters.escape_string(
                "INSERT INTO {}(player_data, player_id, season) value (%s, %s, %s)".format(self._get_mode(cls))
            )
        await cur.execute(command, (self._dump_dict(data.data), player_id, season))
        await self.commit()
        await cur.close()
        return

    async def get_play_data(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        season = season.id if isinstance(season, Season) else season
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cur = await self.database.get_cursor(aiomysql.cursors.DictCursor)
        command = pymysql.converters.escape_string(
            "SELECT player_data FROM {} WHERE player_id = %s AND season = %s".format(self._get_mode(cls))
        )
        await cur.execute(command, (player_id, season))
        data = await cur.fetchone()
        result = self._load_dict(data.get("player_data")) if data is not None else None
        await cur.close()
        return result

    async def _playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ) -> Optional[GameModeReceive]:
        _player = self.pubg.player_id(player_id)
        for i in range(5):
            try:
                if cls == player.SeasonStats:
                    data = await _player.season_stats(season)
                elif cls == player.RankedStats:
                    data = await _player.ranked_stats(season)
                else:
                    raise ValueError("{} is not found".format(cls))
                break
            except TooManyRequests as error:
                timer = (error.reset - self.time()).total_seconds()
                if timer < 0:
                    continue

                if self.too_much_callback is not None:
                    await self.too_much_callback(error=error, index=i)
                else:
                    await asyncio.sleep(error.reset)
        else:
            return
        return data

    async def get_playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        if self.database is None:
            await self.get_database()
        data = await self.get_play_data(player_id=player_id, cls=cls, season=season)
        last_update = await self.get_lastupdate(player_id=player_id, cls=cls)
        if data is None or data == {} or (self.time() - last_update).days >= 2:
            new_data = True if data is None or data else False
            data = await self._playdata(player_id=player_id, cls=cls, season=season)
            if data is None:
                return

            if new_data:
                await self.save_play_data(player_id=player_id, season=season, data=data, update=False)
            else:
                await self.save_play_data(player_id=player_id, season=season, data=data, update=True)

            await self.save_lastupdate(player_id=player_id, cls=cls, dt=self.time())
        if isinstance(data, dict):
            data = GameModeReceive(data, cls)
        return data

    async def update_playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        if self.database is None:
            await self.get_database()
        data = await self._playdata(player_id=player_id, cls=cls, season=season)
        if data is None:
            return
        await self.save_play_data(player_id=player_id, season=season, data=data, update=True)
        await self.save_lastupdate(player_id=player_id, cls=cls, dt=self.time())
        return data


class CacheMatchesList(CacheData):
    def __init__(self, client: Client):
        super().__init__(client)

    async def save_matches_lists(
            self,
            player_id: Union[str, player.Player],
            data: List[str],
            update: bool = False
    ):
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        await self.database.update(
            table="player_data",
            key_name="player_id",
            key=player_id,
            value={
                "matches_data": self._dump_dict(data)
            }
        )
        await self.commit()
        return

    async def get_matches_lists(
            self,
            player_id: Union[str, player.Player]
    ):
        if self.database is None:
            await self.get_database()
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        data = await self.database.query(
            table="player_data",
            key_name="player_id",
            key=player_id,
            filter_col=["matches_data"]
        )
        result = self._load_dict(data.get("matches_data")) if data is not None else None
        return result

    async def get_matches(
            self,
            player_id: Union[str, player.Player]
    ):
        if self.database is None:
            await self.get_database()
        data = await self.get_matches_lists(player_id=player_id)
        last_update = await self.get_lastupdate(player_id=player_id, cls=player.Player)
        if data is None or data == [] or data == {} or (self.time() - last_update).days >= 2:
            _player: List[player.Player] = await self.pubg.players(ids=[player_id])
            data = _player[0].matches
            await self.save_matches_lists(player_id=player_id, data=data)

            await self.save_lastupdate(player_id=player_id, cls=player.Player, dt=self.time())
        return data

    async def update_matches(
            self,
            player_id: Union[str, player.Player]
    ):
        if self.database is None:
            await self.get_database()
        _player: List[player.Player] = await self.pubg.players(ids=[player_id])
        data = _player[0].matches
        await self.save_matches_lists(player_id=player_id, data=data, update=True)
        await self.save_lastupdate(player_id=player_id, cls=player.Player, dt=self.time())
        return data


class CacheMatches(CacheData):
    def __init__(self, client: Client):
        super().__init__(client)

    async def save_matches(
            self,
            matches_id: str,
            data: Matches
    ):
        await self.database.insert(
            table=self._get_mode(Matches),
            value={
                "match_data": self._dump_dict(data.data),
                "included_data": self._dump_dict(data.included),
                "match_id": matches_id
            }
        )
        await self.commit()
        return

    async def get_matches(
            self,
            matches_id: str
    ):
        if self.database is None:
            await self.get_database()
        data = await self.database.query(
            table=self._get_mode(Matches),
            key_name="match_id",
            key=matches_id,
            filter_col=["match_data", "included_data"]
        )
        result1 = self._load_dict(data.get("match_data")) if data is not None else None
        result2 = self._load_dict(data.get("included_data")) if data is not None else None
        return {"data": result1, "included": result2}

    async def get_match(
            self,
            matches_id: str
    ):
        if self.database is None:
            await self.get_database()
        data: Optional[dict] = await self.get_matches(matches_id=matches_id)
        if data is None or data == {"data": None, "included": None}:
            data: Matches = await self.pubg.matches(matches_id)
            await self.save_matches(matches_id=matches_id, data=data)
            return data
        return Matches(data["data"], data["included"])
