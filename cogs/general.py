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
from sqlalchemy.orm import sessionmaker

from config.config import get_config

parser = get_config()


class General:
    def __init__(self, bot):
        self.client: discord.AutoShardedClient = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @interaction.command(description="PUBG BOT의 핑(상태)을 확인합니다.")
    async def ping(self, ctx: interaction.ApplicationContext):
        datetime_now_for_read = datetime.datetime.now(tz=datetime.timezone.utc)
        response_ping_r = ctx.created_at - datetime_now_for_read
        response_ping_read = abs(
            round(response_ping_r.total_seconds() * 1000, 2)
        )
        first_latency = round(self.client.latency * 1000, 2)
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n응답속도(읽기): {round(response_ping_read, 2)}ms",
            color=self.color,
        )
        msg = await ctx.send(embed=embed)
        datetime_now_for_write = datetime.datetime.now(tz=datetime.timezone.utc)
        response_ping_w = datetime_now_for_write - msg.created_at
        response_ping_write = abs(round(response_ping_w.total_seconds() * 1000, 2))
        embed = discord.Embed(
            title="Pong!",
            description=f"클라이언트 핑상태: {first_latency}ms\n"
            f"응답속도(읽기/쓰기): {round(response_ping_read, 2)}ms/{round(response_ping_write, 2)}ms",
            color=self.color,
        )
        await msg.edit(embed=embed)
        return

    @interaction.command(name="정보", description="PUBG BOT의 정보를 확인합니다.")
    async def information(self, ctx: interaction.ApplicationContext):
        total = 0
        for i in self.client.guilds:
            total += i.member_count
        embed = discord.Embed(title="PUBG BOT", color=self.color)
        embed.add_field(
            name="개발", value="[건유1019#0001](https://discord.gg/mr6RpUeG96)", inline=True
        )
        embed.add_field(
            name="<:user:735138021850087476>서버수 / 유저수",
            value=f'{format(len(self.client.guilds), ",")}서버/{format(total, ",")}명',
            inline=True,
        )
        embed.add_field(
            name="이용 약관", value=f"[통합 이용약관](https://pubg.yhs.kr/term)", inline=True
        )
        embed.add_field(
            name="PUBG BOT 버전", value=f'{parser.get("Default","version")}', inline=True
        )
        if ctx.guild is not None and self.client.shard_count is not None:
            embed.add_field(
                name="샤드 ID(샤드 갯수)",
                value=f"#{ctx.guild.shard_id} ({self.client.shard_count}개)",
                inline=True,
            )
        embed.set_thumbnail(url=self.client.user.avatar.url)
        await ctx.send(embed=embed)
        return

    @interaction.command(name="도움말", description='PUBG BOT의 사용 방법을 불러옵니다.')
    async def help(self, ctx):
        help_command = Help(
                ctx=ctx,
                client=self.client
        )
        await help_command.first_page()
        return


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(General(client))
