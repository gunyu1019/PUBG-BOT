import pymysql
import json
from datetime import datetime
from typing import Union, Type, Optional, List

from config.config import parser
from utils.database import get_database
from module.pubgpy import player, Client, Season, GameModeReceive, Matches
from module.errors import InvalidArgument


class CacheData:
    def __init__(self, client: Client):
        self.database = get_database()
        self.pubg = client

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
        return self.database.close()

    @staticmethod
    def _dump_dict(data: Union[dict, list]) -> str:
        return json.dumps(data, indent=4)

    @staticmethod
    def _load_dict(data: Optional[str]) -> Union[dict, list]:
        if data is None:
            return {}
        return json.loads(data)

    def save_lastupdate(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats, player.Player]],
            dt: datetime
    ):
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        command = pymysql.escape_string(
            "UPDATE player_data SET {} = %s WHERE player_id = %s".format(self._get_last_update(cls))
        )
        cur.execute(command, (dt.strftime("%Y-%m-%d %H:%M:%S"), player_id))
        self.commit()
        cur.close()
        return

    def get_lastupdate(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats, player.Player]]
    ) -> Optional[datetime]:
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        command = pymysql.escape_string(
            "SELECT {} FROM player_data WHERE player_id = %s".format(self._get_last_update(cls))
        )
        cur.execute(command, player_id)
        data = cur.fetchone()
        result = data.get(self._get_last_update(cls)) if data is not None else None
        cur.close()
        return result


class CachePlayData(CacheData):
    def __init__(self, client: Client):
        super().__init__(client)

    def save_play_data(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            data: player.GameModeReceive,
            update: bool = False
    ):
        season = season.id if isinstance(season, Season) else season
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cls = data.type_class
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        if update:
            command = pymysql.escape_string(
                "UPDATE {} SET player_data=%s WHERE player_id=%s and season = %s".format(self._get_mode(cls))
            )
        else:
            command = pymysql.escape_string(
                "INSERT INTO {}(player_data, player_id, season) value (%s, %s, %s)".format(self._get_mode(cls))
            )
        cur.execute(command, (self._dump_dict(data.data), player_id, season))
        self.commit()
        cur.close()
        return

    def get_play_data(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        season = season.id if isinstance(season, Season) else season
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        command = pymysql.escape_string(
            "SELECT player_data FROM {} WHERE player_id = %s AND season = %s".format(self._get_mode(cls))
        )
        cur.execute(command, (player_id, season))
        data = cur.fetchone()
        result = self._load_dict(data.get("player_data")) if data is not None else None
        cur.close()
        return result

    async def _playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ) -> GameModeReceive:
        _player = self.pubg.player_id(player_id)
        if cls == player.SeasonStats:
            data = await _player.season_stats(season)
        elif cls == player.RankedStats:
            data = await _player.ranked_stats(season)
        else:
            raise InvalidArgument("{} is not found".format(cls))
        return data

    async def get_playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        data = self.get_play_data(player_id=player_id, cls=cls, season=season)
        last_update = self.get_lastupdate(player_id=player_id, cls=cls)
        if data is None or data == {} or (datetime.now() - last_update).days >= 2:
            _player = self.pubg.player_id(player_id)
            new_data = True if data is None or data else False
            data = await self._playdata(player_id=player_id, cls=cls, season=season)

            if new_data:
                self.save_play_data(player_id=player_id, season=season, data=data, update=False)
            else:
                self.save_play_data(player_id=player_id, season=season, data=data, update=True)

            self.save_lastupdate(player_id=player_id, cls=cls, dt=datetime.now())
        if isinstance(data, dict):
            data = GameModeReceive(data, cls)
        return data

    async def update_playdata(
            self,
            player_id: Union[str, player.Player],
            season: Union[str, Season],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        data = await self._playdata(player_id=player_id, cls=cls, season=season)
        self.save_play_data(player_id=player_id, season=season, data=data, update=True)
        self.save_lastupdate(player_id=player_id, cls=cls, dt=datetime.now())
        return data


class CacheMatchesList(CacheData):
    def __init__(self, client: Client):
        super().__init__(client)

    def save_matches_lists(
            self,
            player_id: Union[str, player.Player],
            data: List[str],
            update: bool = False
    ):
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        if update:
            command = pymysql.escape_string(
                "UPDATE player_data SET matches_data=%s WHERE player_id=%s"
            )
        else:
            command = pymysql.escape_string(
                "INSERT INTO player_data(matches_data, player_id) value (%s, %s)"
            )
        cur.execute(command, (self._dump_dict(data), player_id))
        self.commit()
        cur.close()
        return

    def get_matches_lists(
            self,
            player_id: Union[str, player.Player]
    ):
        player_id = player_id.id if isinstance(player_id, player.Player) else player_id
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        command = pymysql.escape_string(
            "SELECT matches_data FROM player_data WHERE player_id = %s"
        )
        cur.execute(command, player_id)
        data = cur.fetchone()
        result = self._load_dict(data.get("matches_data")) if data is not None else None
        cur.close()
        return result

    async def get_matches(
            self,
            player_id: Union[str, player.Player]
    ):
        data = self.get_matches_lists(player_id=player_id)
        last_update = self.get_lastupdate(player_id=player_id, cls=player.Player)
        if data is None or data == [] or data == {} or (datetime.now() - last_update).days >= 2:
            _player: List[player.Player] = await self.pubg.players(ids=[player_id])
            new_data = True if data is None or data else False
            data = _player[0].matches

            if new_data:
                self.save_matches_lists(player_id=player_id, data=data, update=False)
            else:
                self.save_matches_lists(player_id=player_id, data=data, update=True)

            self.save_lastupdate(player_id=player_id, cls=player.Player, dt=datetime.now())
        return data

    async def update_matches(
            self,
            player_id: Union[str, player.Player]
    ):
        _player: List[player.Player] = await self.pubg.players(ids=[player_id])
        data = _player[0].matches
        self.save_matches_lists(player_id=player_id, data=data, update=True)
        self.save_lastupdate(player_id=player_id, cls=player.Player, dt=datetime.now())
        return data


class CacheMatches(CacheData):
    def __init__(self, client: Client):
        super().__init__(client)

    def save_matches(
            self,
            matches_id: str,
            data: Matches
    ):
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        command = pymysql.escape_string(
            "INSERT INTO {}(match_data, included_data, match_id) value (%s, %s, %s)".format(self._get_mode(Matches))
        )
        cur.execute(command, (self._dump_dict(data.data), self._dump_dict(data.included), matches_id))
        self.commit()
        cur.close()
        return

    def get_matches(
            self,
            matches_id: str
    ):
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        command = pymysql.escape_string(
            "SELECT match_data, included_data FROM {} WHERE match_id = %s".format(self._get_mode(Matches))
        )
        cur.execute(command, matches_id)
        data = cur.fetchone()
        result1 = self._load_dict(data.get("match_data")) if data is not None else None
        result2 = self._load_dict(data.get("included_data")) if data is not None else None
        cur.close()
        return {"data": result1, "included": result2}

    async def get_match(
            self,
            matches_id: str
    ):
        data: Optional[dict] = self.get_matches(matches_id=matches_id)
        if data is None or data == {"data": None, "included": None}:
            data: Matches = await self.pubg.matches(matches_id)
            self.save_matches(matches_id=matches_id, data=data)
            return data
        return Matches(data["data"], data["included"])
