"""GNU GENERAL PUBLIC LICENSE

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

import discord
import io

from matplotlib import pyplot as plt
from typing import Union

import pymysql.cursors

from module import commands
from module.interaction import SlashContext, Message
from utils.database import get_database


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619

    @commands.command(name="상태", permission=4)
    async def status(self, ctx: Union[SlashContext, Message]):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT id, date, data FROM SERVER_DATA")
        data = cur.fetchall()

        datetime = [i.get("date").strftime('%H:%M') for i in data]
        players = [i.get("data", 0) for i in data]

        plt.clf()
        plt.title('Online Players')
        plt.plot(datetime, players, color='blue', marker='o', label='Online Players')
        plt.xlabel('time')
        plt.ylabel('user')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = discord.File(buf, filename="status.png")

        embed = discord.Embed(color=0xffd619)
        embed.add_field(name="동접자수:", value="{}명 유저가 플레이 중입니다.".format(players[0]), inline=True)
        embed.set_image(url="attachment://status.png")
        await ctx.send(file=file, embed=embed)
        return


def setup(client):
    return Command(client)
