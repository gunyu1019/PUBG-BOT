import logging
import sys

import DBSkr
import discord
from discord.ext import commands

from utils import token

logger = logging.getLogger(__name__)
DBS = None


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
        global DBS
        DBS = DBSkr.Client(self.bot, koreanbots_token=token.DBKR_token, topgg_token=token.DBL_token, autopost=True)

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
    async def on_error(self, event, *args, **_):
        if event == "on_message":
            message = args[0]
            exc = sys.exc_info()
            excname = exc[0].__name__
            excarglist = [str(x) for x in exc[1].args]

            def traceback_msg(tb):
                if tb.tb_next is None:
                    return f"{tb.tb_frame.f_code.co_filename} {tb.tb_frame.f_code.co_name} {tb.tb_lineno}줄 "
                return f"{tb.tb_frame.f_code.co_filename} ({tb.tb_frame.f_code.co_name}) {tb.tb_lineno}줄\n{traceback_msg(tb.tb_next)}"

            error_location = traceback_msg(exc[2])
            if not excarglist:
                errerlog = excname
            else:
                errerlog = excname + ": " + ", ".join(excarglist)
            if message.channel.type != discord.ChannelType.private:
                logger.error(
                    f"({message.guild.name},{message.channel.name},{message.author},{message.content}): {errerlog}\n{error_location}")
            else:
                logger.error(f"({message.channel},{message.author},{message.content}): {errerlog}\n{error_location}")
            embed = discord.Embed(title="\U000026A0 에러", color=0x070ff)
            embed.add_field(name='에러 내용(traceback)', value=f'{errerlog}', inline=False)
            embed.add_field(name='에러 위치', value=f'{error_location}', inline=False)
            if message.channel.type != discord.ChannelType.private:
                embed.add_field(name='서버명', value=f'{message.guild.name}', inline=True)
                embed.add_field(name='채널명', value=f'{message.channel.name}', inline=True)
            embed.add_field(name='유저명', value=f'{message.author}', inline=True)
            embed.add_field(name='메세지', value=f'{message.content}', inline=False)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.guild is not None:
            logger.info(f"({ctx.guild} | {ctx.channel} | {ctx.author}) {ctx.message.content}")
        else:
            logger.info(f"(DM채널 | {ctx.author}) {ctx.message.content}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if error.__class__ == discord.ext.commands.errors.CommandNotFound:
            return
        elif error.__class__ == discord.ext.commands.CheckFailure:
            embed = discord.Embed(title="\U000026A0 에러", description="권한이 부족합니다.", color=0xaa0000)
            await ctx.send(embed=embed)
            return

        excname = str(type(error.original))
        excarglist = [str(x) for x in error.original.args]

        def traceback_msg(tb):
            if tb.tb_next is None:
                return f"{tb.tb_frame.f_code.co_filename} {tb.tb_frame.f_code.co_name} {tb.tb_lineno}줄 "
            return f"{tb.tb_frame.f_code.co_filename} ({tb.tb_frame.f_code.co_name}) {tb.tb_lineno}줄\n{traceback_msg(tb.tb_next)}"

        error_location = traceback_msg(error.original.__traceback__)
        if not excarglist:
            errerlog = excname
        else:
            errerlog = excname + ": " + ", ".join(excarglist)
        if ctx.channel.type != discord.ChannelType.private:
            logger.error(
                f"({ctx.guild.name}, {ctx.channel.name}, {ctx.author}, {ctx.message.content}): {errerlog}\n{error_location}")
        else:
            logger.error(f"({ctx.channel}, {ctx.author}, {ctx.message.content}): {errerlog}\n{error_location}")
        embed = discord.Embed(title="\U000026A0 에러", color=0x0070ff)
        embed.add_field(name='에러 내용(traceback)', value=f'{errerlog}', inline=False)
        embed.add_field(name='에러 위치', value=f'{error_location}', inline=False)
        if ctx.channel.type != discord.ChannelType.private:
            embed.add_field(name='서버명', value=f'{ctx.guild.name}', inline=True)
            embed.add_field(name='채널명', value=f'{ctx.channel.name}', inline=True)
        embed.add_field(name='유저명', value=f'{ctx.author}', inline=True)
        embed.add_field(name='메세지', value=f'{ctx.message.content}', inline=False)


def setup(client):
    client.add_cog(Events(client))
