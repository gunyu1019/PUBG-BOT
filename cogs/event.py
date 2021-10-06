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
from typing import Union

from module.interaction import ApplicationContext
from module.message import MessageCommand
from utils import token

logger = logging.getLogger(__name__)
logger_command = logging.getLogger(__name__ + ".command")
logger_guild = logging.getLogger(__name__ + ".guild")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        DBSkr.Client(
            self.bot,
            koreanbots_token=token.koreanBots_token,
            topgg_token=token.DBL_token,
            uniquebots_token=token.uniqueBots_token,
            autopost=True
        )

        self.bot.prefix_class.load_prefixes()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_number = None
        for i in self.bot.guilds:
            if i.name == guild.name:
                server_number = self.bot.guilds.index(i) + 1
        if server_number is not None:
            logger_guild.info(
                guild.name + '에 가입이 확인되었습니다. 서버번호: ' + str(server_number) + '번, 서버멤버' + str(guild.member_count) + '명')
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        logger_guild.info(guild.name + '로 부터 추방 혹은 차단되었습니다.')
        return

    @commands.Cog.listener()
    async def on_command(self, ctx: Union[ApplicationContext, MessageCommand]):
        if ctx.guild is not None:
            logger_command.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.content}")
        else:
            logger_command.info(f"(DM채널 | {ctx.author}) {ctx.content}")


def setup(client):
    client.add_cog(Events(client))
