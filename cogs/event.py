import logging

import DBSkr
import discord
from discord.ext import commands
from typing import Union

from module.interaction import SlashContext, Message
from utils import token

logger = logging.getLogger(__name__)


def log_system(msg):
    logger.info(msg)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_system(f'디스코드 봇 로그인이 완료되었습니다.')
        log_system(f"디스코드봇 이름: {self.bot.user.name}")
        log_system(f"디스코드봇 ID: {str(self.bot.user.id)}")
        log_system(f"디스코드봇 버전: {discord.__version__}")
        print('------------')
        answer = ""

        total = 0
        for i in range(len(self.bot.guilds)):
            answer = answer + str(i + 1) + "번째: " + str(self.bot.guilds[i]) + "(" + str(
                self.bot.guilds[i].id) + "):" + str(
                self.bot.guilds[i].member_count) + "명\n"
            total += self.bot.guilds[i].member_count
        log_system(f"방목록: \n{answer}\n방의 종합 멤버:{total}명")

        log_system(f'DBSkr이 실행됩니다.')
        dbs = logging.getLogger("DBSkr")
        dbs.setLevel(logging.DEBUG)
        DBSkr.Client(
            self.bot,
            koreanbots_token=token.koreanBots_token,
            topgg_token=token.DBL_token,
            uniquebots_token=token.uniqueBots_token,
            autopost=True
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_number = None
        for i in self.bot.guilds:
            if i.name == guild.name:
                server_number = self.bot.guilds.index(i) + 1
        if server_number is not None:
            log_system(
                guild.name + '에 가입이 확인되었습니다. 서버번호: ' + str(server_number) + '번, 서버멤버' + str(guild.member_count) + '명')
        return

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        log_system(guild.name + '로 부터 추방 혹은 차단되었습니다.')
        return

    @commands.Cog.listener()
    async def on_command(self, ctx: Union[SlashContext, Message]):
        if ctx.guild is not None:
            logger.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.content}")
        else:
            logger.info(f"(DM채널 | {ctx.author}) {ctx.content}")


def setup(client):
    client.add_cog(Events(client))
