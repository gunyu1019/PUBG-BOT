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

import io

import discord
from datetime import timezone
from discord.ext import interaction
from matplotlib import font_manager
from matplotlib import pyplot as plt

from config.config import parser
from module.player_data import PlayerData
from utils.database import get_database
from utils.permission import permission
from utils.directory import directory


class Server:
    def __init__(self, bot):
        self.client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)
        self.data = PlayerData(loop=self.client.loop)

    @interaction.command(name="상태", description='배틀그라운드(스팀) 서버의 상태를 불러옵니다.')
    @permission(4)
    async def status(self, ctx: interaction.ApplicationContext):
        await ctx.defer()
        connect = await get_database()
        data = await connect.query_all(
            table="SERVER_DATA",
            filter_col=['id', 'date', 'data']
        )

        datetime = [i.get("date").replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%H:%M') for i in data]
        players = [i.get("data", 0) for i in data]
        await connect.close()

        plt.clf()
        font_path = f"{directory}/assets/Font/NotoSansKR-Bold.otf"
        font_title = font_manager.FontProperties(fname=font_path, size=15)

        ax = plt.axes()
        ax.tick_params(axis='both', colors='white')
        ax.set_facecolor('#32353b')

        plt.title('실시간 동접자 수', color='white', fontweight="bold", fontproperties=font_title)
        plt.plot(datetime, players, color='#b0beff', marker='o', label='Online Players')
        plt.xlabel('Time', color='white')
        plt.ylabel('Users', color='white')
        plt.fill_between(datetime, players, alpha=0.5, color='#b0beff')
        plt.grid(True, axis='both', color="#2f3136", alpha=0.5, linestyle='--')
        plt.xlim([1, len(datetime) - 1])
        plt.ylim(bottom=1)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor="#2f3136")
        buf.seek(0)
        file = discord.File(buf, filename="status.png")

        status, player = await self.data.get_data()
        if not status:
            player = players[-1]

        embed = discord.Embed(color=self.color)
        embed.add_field(name="동접자수:", value="{}명 유저가 플레이 중입니다.".format(format(player, ',')), inline=True)
        embed.set_image(url="attachment://status.png")
        await ctx.send(file=file, embed=embed)
        return


def setup(client):
    return client.add_interaction_cog(Server(client))
