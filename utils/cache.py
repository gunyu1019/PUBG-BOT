import pymysql
import json
from datetime import datetime
from typing import Union, Type, Optional

from config.config import parser
from utils.database import getDatabase
from module.pubgpy import player, Client, Season, GameModeReceive
from module.errors import InvalidArgument


class CacheData:
    def __init__(self, client: Client):
        self.database = getDatabase()
        self.pubg = client

    @staticmethod
    def _get_mode(cls) -> Optional[str]:
        if cls == player.SeasonStats:
            return parser.get("DatabaseName", "SeasonStats")
        elif cls == player.RankedStats:
            return parser.get("DatabaseName", "RankedStats")

    @staticmethod
    def _get_last_update(cls) -> Optional[str]:
        if cls == player.SeasonStats:
            return "season_date"
        elif cls == player.RankedStats:
            return "ranked_date"

    def commit(self):
        return self.database.commit()

    def close(self):
        return self.database.close()

    @staticmethod
    def _dump_dict(data: dict) -> str:
        return json.dumps(data, indent=4)

    @staticmethod
    def _load_dict(data: Optional[str]) -> dict:
        if data is None:
            return {}
        return json.loads(data)

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

    def save_lastupdate(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats]],
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
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
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
        return GameModeReceive(data, cls) if not isinstance(data, GameModeReceive) else data

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
