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

import logging

import DBSkr
import discord
from discord.ext import commands
from discord.ext import interaction

from config.config import parser
from utils import token

logger = logging.getLogger(__name__)
logger_command = logging.getLogger(__name__ + ".command")
logger_guild = logging.getLogger(__name__ + ".guild")


class Events:
    def __init__(self, bot):
        self.bot = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'디스코드 봇 로그인이 완료되었습니다.')
        logger.info(f"디스코드봇 이름: {self.bot.user.name}")
        logger.info(f"디스코드봇 ID: {str(self.bot.user.id)}")
        logger.info(f"디스코드봇 버전: {discord.__version__}")
        print('------------')
        answer = ""

        total = 0
        for i in range(len(self.bot.guilds)):
            answer = answer + str(i + 1) + "번째: " + str(self.bot.guilds[i]) + "(" + str(
                self.bot.guilds[i].id) + "):" + str(
                self.bot.guilds[i].member_count) + "명\n"
            total += self.bot.guilds[i].member_count
        logger.info(f"방목록: \n{answer}\n방의 종합 멤버:{total}명")

        logger.info(f'DBSkr이 실행됩니다.')
        dbs = logging.getLogger("DBSkr")
        dbs.setLevel(logging.DEBUG)
        if self.bot.user.id == 704683198164238446:
            DBSkr.Client(
                self.bot,
                koreanbots_token=token.koreanBots_token,
                topgg_token=token.DBL_token,
                autopost=True
            )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_number = None
        for i in self.bot.guilds:
            if i.name == guild.name:
                server_number = self.bot.guilds.index(i) + 1
        if server_number is not None:
            logger_guild.info(
                guild.name + '에 가입이 확인되었습니다. 서버번호: ' + str(server_number) + '번, 서버멤버' + str(guild.member_count) + '명')

        await (
            self.bot.get_guild(786153760824492062)
                .get_channel(938656148423344178)
                .send(
                "새로운 서버에 추가되었습니다. **(현재 서버수 : {0})**".format(self.bot.guilds)
            )
        )
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger_guild.info(guild.name + '로 부터 추방 혹은 차단되었습니다.')
        return

    @commands.Cog.listener()
    async def on_interaction_command(self, ctx: interaction.ApplicationContext):
        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.content}")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if not isinstance(ctx, commands.Context):
            return

        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.message.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.message.content}")

    @commands.Cog.listener()
    async def on_components_cancelled(self, ctx: interaction.ComponentsContext):
        embed = discord.Embed(
            title="\U000026A0 안내",
            description="상호작용을 찾을 수 없습니다. 명령어로 기능을 통하여 다시 이용해 주시기 바랍니다.",
            color=self.warning_color
        )
        embed.add_field(
            name="왜 상호작용을 찾을 수 없나요?",
            value="상호작용을 찾을 수 없는 대표적 이유는 `대기 시간초과(5분)`이 있습니다. "
                  "이외에도 특정 서버에 전적, 매치 등의 동적 명령어를 과도하게 사용할 경우 최상위에 있던 메시지의 상호작용이 우선 종료됩니다.",
            inline=False
        )
        await ctx.send(embed=embed, hidden=True)
        return


def setup(client):
    client.add_icog(Events(client))
