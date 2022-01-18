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
along with PUBG BOT.  If not, see <https://www.gnu.org/licenses/>.
"""

import datetime

import discord
from discord.ext import interaction

from config.config import parser
from process.help import Help
from utils.permission import permission


class General:
    def __init__(self, bot):
        self.client: discord.Client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @interaction.command(description='PUBG BOT의 핑(상태)을 확인합니다.')
    @permission(4)
    async def ping(self, ctx: interaction.ApplicationContext):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if ctx.created_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        if now > ctx.created_at:
            response_ping_r = now - ctx.created_at
        else:
            response_ping_r = ctx.created_at - now
        response_ping_read = float(str(response_ping_r.seconds) + "." + str(response_ping_r.microseconds))
        first_latency = round(self.client.latency * 1000, 2)
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n응답속도(읽기): {round(response_ping_read * 1000, 2)}ms",
            color=self.color)
        msg = await ctx.send(embed=embed)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if ctx.created_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        if now > msg.created_at:
            response_ping_w = now - msg.created_at
        else:
            response_ping_w = msg.created_at - now
        response_ping_write = float(str(response_ping_w.seconds) + "." + str(response_ping_w.microseconds))
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n응답속도(읽기/쓰기): {round(response_ping_read * 1000, 2)}ms/{round(response_ping_write * 1000, 2)}ms",
            color=self.color)
        await msg.edit(embed=embed)
        return

    @interaction.command(name='정보', description='PUBG BOT의 정보를 확인합니다.')
    @permission(4)
    async def information(self, ctx):
        total = 0
        for i in self.client.guilds:
            total += i.member_count
        embed = discord.Embed(title='PUBG BOT', color=self.color)
        embed.add_field(name='개발', value='[건유1019#0001](https://yhs.kr/YBOT/forum.html)', inline=True)
        embed.add_field(name='<:user:735138021850087476>서버수 / 유저수', value=f'{len(self.client.guilds)}서버/{total}명', inline=True)
        embed.add_field(name='PUBG BOT 버전', value=f'{parser.get("DEFAULT","version")}', inline=True)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)
        return

    @interaction.command(name="도움말", description='PUBG BOT의 사용 방법을 불러옵니다.')
    @permission(4)
    async def help(self, ctx):
        help_command = Help(
                ctx=ctx,
                client=self.client
        )
        await help_command.first_page()
        return


def setup(client):
    return client.add_icog(General(client))
