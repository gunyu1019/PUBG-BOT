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

import datetime
import logging

import pymysql
from discord.ext import tasks

from module.player_data import PlayerData
from utils.database import get_database

log = logging.getLogger(__name__)


class GraphTask:
    def __init__(self, bot):
        self.bot = bot

        logging.info("Steam Player Data Task has begun.")
        self.client = PlayerData(loop=self.bot.loop)
        self.check_player.start()

    @tasks.loop(minutes=10)
    async def check_player(self):
        time_now = datetime.datetime.now()
        connect = get_database()
        cur = connect.cursor()

        sql_v2_ck = "SELECT date FROM SERVER_DATA WHERE ID=12"
        cur.execute(sql_v2_ck)
        lasted_update = cur.fetchone()[0]
        if (time_now - lasted_update).seconds >= 3600:
            status, players = await self.client.get_data()
            if status:
                for i in range(12):
                    sql_v2_ps = "UPDATE SERVER_DATA SET id=%s WHERE id=%s"
                    cur.execute(sql_v2_ps, (i, i + 1))

                sql_v2_pd = "DELETE FROM SERVER_DATA WHERE ID=0"
                sql_v2_pc = pymysql.escape_string("INSERT INTO SERVER_DATA(data, date, id) VALUES(%s, %s, 12)")
                cur.execute(sql_v2_pd)
                cur.execute(sql_v2_pc, (int(players), time_now.strftime('%Y-%m-%d %H:%M:%S')))
                logging.info("Update of player data successful. Time: {0},Player: {1}".format(
                    time_now.strftime('%H:%M'), players
                ))
            else:
                logging.info("Update of player data failed. Time: {0}".format(time_now.strftime('%H:%M')))
        connect.commit()
        connect.close()

    @check_player.before_loop
    async def before_booting(self):
        await self.bot.wait_until_ready()


def setup(client):
    client.add_icog(GraphTask(client))
