import pymysql
from typing import Union, Type, Optional

from config.config import parser
from utils.database import getDatabase
from module.pubgpy import player, Client


class CacheData:
    def __init__(self, client: Client):
        self.database = getDatabase()

    @staticmethod
    def _get_mode(cls) -> Optional[str]:
        if cls == player.SeasonStats:
            return parser.get("DatabaseName", "SeasonStats")
        elif cls == player.RankedStats:
            return parser.get("DatabaseName", "RankedStats")

    def commit(self):
        return self.database.commit()

    def close(self):
        return self.database.close()

    def save_play_data(
            self,
            player_id: Union[str, player.Player],
            data: player.GameModeReceive,
            update: bool = False
    ):
        cls = data.type_class
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        if update:
            command = pymysql.escape_string("UPDATE %s SET player_data=%s WHERE player_id=%s")
        else:
            command = pymysql.escape_string("INSERT INTO %s(player_data, player_id) value (%s, %s)")
        cur.execute(command, (self._get_mode(cls), player_id, data.data))
        return

    def get_play_data(
            self,
            player_id: Union[str, player.Player],
            cls: Type[Union[player.SeasonStats, player.RankedStats]]
    ):
        cur = self.database.cursor(pymysql.cursors.DictCursor)
        command = pymysql.escape_string("SELECT player_data FROM %s WHERE player_id = %s")
        cur.execute(command, (self._get_mode(cls), player_id))
        return
