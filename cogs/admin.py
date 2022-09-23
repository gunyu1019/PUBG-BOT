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

import ast
import os
import asyncio
import datetime
import platform
import traceback

import discord
from discord.ext import interaction

from config.config import parser
from utils.directory import directory
from utils.permission import is_owner


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Admin:
    def __init__(self, bot: interaction.Client):
        self.client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

    @interaction.listener()
    async def on_interaction_message(self, message: interaction.Message):
        prefixes = ("!", f"<@{self.client.user.id}>", f"<@!{self.client.user.id}>")
        if (
            not message.content.startswith(prefixes) or
            not is_owner(message.author.id)
        ):
            return

        command = ""
        for prefix in prefixes:
            if message.content.startswith(prefix):
                command = message.content[len(prefix):]
                break

        if command.startswith("debug"):
            await self.debug(message)
        elif command.startswith("cmd"):
            await self.cmd(message)
        if command.startswith("reload"):
            await self.reload(message)
        return

    async def debug(self, ctx):
        list_message = ctx.content.split()
        if len(list_message) < 1:
            embed = discord.Embed(title="PUBG BOT 도우미", description='사용하실 커맨드를 작성해주세요.', color=self.color)
            await ctx.send(embed=embed)
            return
        cmd = " ".join(list_message[1:])
        if cmd.startswith("```") and cmd.endswith("```"):
            cmd = cmd[3:-3]
            if cmd.startswith("py"):
                cmd = cmd[2:]
        before_cmd = cmd
        time1 = datetime.datetime.now()

        embed = discord.Embed(title="Debugging", color=self.color)
        embed.add_field(name="입력", value=f"```py\n{before_cmd}\n```", inline=False)
        embed.add_field(name="출력", value="```py\nevaling...\n```", inline=False)
        embed.add_field(name="출력(Type)", value="```py\nevaling...\n```", inline=False)
        embed.add_field(name="소요시간", value="```\ncounting...\n```", inline=False)
        msg = await ctx.send(embed=embed)
        try:
            fn_name = "__eval"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():{cmd}"
            parsed = ast.parse(body)
            body = getattr(parsed.body[0], "body", "")
            insert_returns(body)
            env = {
                "self": self,
                "bot": self.client,
                "discord": discord,
                "ctx": ctx,
                "interaction": interaction,
                "channel": ctx.channel,
                "author": ctx.author,
                "server": ctx.guild,
                "__import__": __import__,
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)
            time2 = datetime.datetime.now()
            microsecond = (round(float(f"0.{(time2 - time1).microseconds}"), 3))
            second = (time2 - time1).seconds
            try:
                embed.set_field_at(1, name="출력", value=f"```py\n{result}\n```", inline=False)
                embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(result)}\n```", inline=False)
                embed.set_field_at(3, name="소요시간", value=f"```\n{second + microsecond}초\n```", inline=False)
                await msg.edit(embed=embed)
            except discord.errors.HTTPException:
                with open("debug_result.txt", "w") as f:
                    f.write(f"debug : \n{cmd}\n-----\n{result}")
                embed.set_field_at(1, name="출력",
                                   value="```length of result is over 1000. here is text file of result```",
                                   inline=False)
                embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(result)}\n```", inline=False)
                embed.set_field_at(3, name="소요시간", value=f"```\n{second + microsecond}초\n```", inline=False)
                await msg.edit(embed=embed)
                await ctx.send(file=discord.File("debug_result.txt"))
        except Exception as e:
            embed.set_field_at(1, name="출력", value=f"```pytb\n{traceback.format_exc()}\n```", inline=False)
            embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(e)}\n```", inline=False)
            embed.set_field_at(3, name="소요시간", value=f"```\n동작 중단\n```", inline=False)
            await msg.edit(embed=embed)
        return

    async def cmd(self, ctx):
        list_message = ctx.content.split()
        if len(list_message) < 1:
            embed = discord.Embed(
                title="PUBG BOT 도우미",
                description="!=cmd <명령어>\n명령어를 입력해주세요!",
                color=self.color
            )
            await ctx.send(embed=embed)
            return
        cmd = " ".join(list_message[1:])
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        if platform.system() == "Windows":
            decode = 'cp949'
        else:
            decode = 'UTF-8'
        stdout, stderr = await proc.communicate()
        if stderr.decode(decode) == "":
            embed = discord.Embed(title="cmd", description=stdout.decode(decode), color=self.color)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="에러!", description=stderr.decode(decode), color=self.color)
            await ctx.send(embed=embed)
        return

    async def reload(self, ctx):
        exts = ["cogs." + file[:-3] for file in os.listdir(f"{directory}/cogs") if file.endswith(".py")]

        embed = discord.Embed(
            title="PUBG BOT",
            description=f"{len(exts)}개의 command와 command.module이 재로딩 중입니다.",
            colour=self.color)
        msg = await ctx.send(embed=embed)
        err = [0, 0, 0]
        e_msg = ""
        for ext in exts:
            try:
                self.client.reload_extension(ext)
            except interaction.ExtensionNotLoaded:
                e_msg += f"\n{ext}를 불러오지 못했습니다."
                err[0] += 1
            except interaction.ExtensionNotFound:
                e_msg += f"\n{ext}를 발견하지 못했습니다."
                err[1] += 1
            except interaction.ExtensionFailed:
                e_msg += f"\n{ext}에 오류가 발생하였습니다."
                err[2] += 1
        embed = discord.Embed(title="PUBG BOT", description=f"{len(exts)}개의 command가 재로딩 되었습니다.", colour=self.color)
        if not e_msg == "":
            embed.description += f"```에러로그(cog): {e_msg}```"
        await msg.edit(embed=embed)
        return


def setup(client):
    return client.add_interaction_cog(Admin(client))
