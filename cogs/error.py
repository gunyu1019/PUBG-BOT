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

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _traceback_msg(self, tb):
        if tb.tb_next is None:
            return f"{tb.tb_frame.f_code.co_filename} {tb.tb_frame.f_code.co_name} {tb.tb_lineno}줄 "
        return f"{tb.tb_frame.f_code.co_filename} ({tb.tb_frame.f_code.co_name}) {tb.tb_lineno}줄\n{self._traceback_msg(tb.tb_next)}"

    @commands.Cog.listener()
    async def on_command_exception(self, ctx, error):
        excname = str(type(error))
        excarglist = [str(x) for x in error.args]

        if not excarglist:
            errerlog = excname
        else:
            errerlog = excname + ": " + ", ".join(excarglist)

        error_location = self._traceback_msg(error.__traceback__)

        if ctx.channel.type != discord.ChannelType.private:
            logger.error(
                f"({ctx.guild.name},{ctx.channel.name},{ctx.author},{ctx.content}): {errerlog}\n{error_location}"
            )
        else:
            logger.error(f"({ctx.channel},{ctx.author},{ctx.content}): {errerlog}\n{error_location}")
        embed = discord.Embed(title="\U000026A0 에러", color=0x070ff)
        embed.add_field(name='에러 내용(traceback)', value=f'{errerlog}', inline=False)
        embed.add_field(name='에러 위치', value=f'{error_location}', inline=False)
        if ctx.channel.type != discord.ChannelType.private:
            embed.add_field(name='서버명', value=f'{ctx.guild.name}', inline=True)
            embed.add_field(name='채널명', value=f'{ctx.channel.name}', inline=True)
        embed.add_field(name='유저명', value=f'{ctx.author}', inline=True)
        embed.add_field(name='메세지', value=f'{ctx.content}', inline=False)
        await self.bot.get_guild(844613188900356157).get_channel(872534703306059806).send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if error.__class__ == discord.ext.commands.errors.CommandNotFound:
            return
        elif error.__class__ == discord.ext.commands.CheckFailure:
            embed = discord.Embed(title="\U000026A0 에러", description="권한이 부족합니다.", color=0xaa0000)
            await ctx.send(embed=embed)
            return


def setup(client):
    client.add_cog(Error(client))
