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
from discord.ext import tasks, interaction

from module.player_data import PlayerData
from utils.database import get_database

log = logging.getLogger(__name__)


class GraphTask:
    def __init__(self, bot: interaction.Client):
        self.bot = bot

        logging.info("Steam Player Data Task has begun.")
        self.bot.add_setup_hook(self.setup_hook)

    async def setup_hook(self):
        self.check_player.start()

    @tasks.loop(minutes=10)
    async def check_player(self):
        time_now = datetime.datetime.utcnow()
        connect = await get_database()
        lasted_update = (await connect.query(
            table="SERVER_DATA",
            key_name='ID', key=12,
            filter_col=['date']
        )).get("date")
        if (time_now - lasted_update).seconds >= 3600:
            status, players = await self.client.get_data()
            if status:
                for i in range(12):
                    await connect.update(
                        table="SERVER_DATA",
                        key_name="id", key=i+1,
                        value={"id": i}
                    )

                await connect.delete(
                    table="SERVER_DATA",
                    key_name="id", key=0
                )
                await connect.insert(
                    table="SERVER_DATA",
                    value={
                        "data": int(players),
                        "date": time_now.strftime('%Y-%m-%d %H:%M:%S'),
                        "id": 12
                    }
                )
                logging.info("Update of player data successful. Time: {0},Player: {1}".format(
                    time_now.strftime('%H:%M'), players
                ))
            else:
                logging.info("Update of player data failed. Time: {0}".format(time_now.strftime('%H:%M')))
        await connect.close(check_commit=True)

    @check_player.before_loop
    async def before_booting(self):
        await self.bot.wait_until_ready()


def setup(client):
    client.add_interaction_cog(GraphTask(client))
