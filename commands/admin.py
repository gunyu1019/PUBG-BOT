import ast
import os
import asyncio
import datetime
import platform
import traceback

import discord
from discord.ext import commands

from module import commands as _command
from utils.database import getDatabase
from utils.perm import check_perm
from utils.prefix import get_prefix
from utils.directory import directory


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619

    @_command.command(aliases=["디버그"], permission=1, interaction=False)
    async def debug(self, ctx):
        list_message = ctx.options
        if len(list_message) < 1:
            embed = discord.Embed(title="PUBG BOT 도우미", description='사용하실 커맨드를 작성해주세요.', color=self.color)
            await ctx.send(embed=embed)
            return
        cmd = " ".join(list_message[0:])
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
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                "self": self,
                "bot": self.client,
                "discord": discord,
                "ctx": ctx,
                "commands": commands,
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
                await ctx.send(file=discord.File("eval_result.txt"))
        except Exception as e:
            embed.set_field_at(1, name="출력", value=f"```pytb\n{traceback.format_exc()}\n```", inline=False)
            embed.set_field_at(2, name="출력(Type)", value=f"```py\n{type(e)}\n```", inline=False)
            embed.set_field_at(3, name="소요시간", value=f"```\n동작 중단\n```", inline=False)
            await msg.edit(embed=embed)
        return

    @_command.command(permission=1, interaction=False)
    async def cmd(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(self.client, ctx)[0]
        if len(list_message) < 1:
            embed = discord.Embed(title="PUBG BOT 도우미", description=prefix + "cmd <명령어>\n명령어를 입력해주세요!", color=self.color)
            await ctx.send(embed=embed)
            return
        search = " ".join(list_message[0:])
        proc = await asyncio.create_subprocess_shell(search,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
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

    @_command.command(name="블랙리스트", permission=9, interaction=False)
    async def blacklist(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(self.client, ctx)[0]
        if len(list_message) < 1:
            embed = discord.Embed(title="PUBG BOT 도우미", description=f"{prefix}블랙리스트 <등록/제거/여부> <맨션(선택)> 와 같이 작성해주세요.",
                                  color=self.color)
            await ctx.send(embed=embed)
            return
        mod = list_message[0]
        if mod == "여부":
            if len(list_message) > 1:
                mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
                member = await ctx.guild.fetch_member(mention)
                if member is None:
                    embed = discord.Embed(title="PUBG BOT 도우미",
                                          description=f"올바른 유저를 기재하여 주세요.",
                                          color=self.color)
                    await ctx.send(embed=embed)
                    return
            else:
                mention = ctx.author.id
            result = check_perm(member)
            if 4 >= result:
                embed = discord.Embed(title="Blacklist!", description="이 사람은 블랙리스트에 등재되어 있지 않습니다.", color=self.color)
            else:
                embed = discord.Embed(title="Blacklist!", description="이 사람은 블랙리스트에 등재되어 있습니다.", color=self.color)
            await ctx.send(embed=embed)
            return
        elif mod == "등록":
            if len(list_message) < 2:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"블랙리스트에 등재할 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await ctx.guild.fetch_member(mention)
            if member is None:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"올바른 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            if 2 < check_perm(ctx.author):
                embed = discord.Embed(title="에러", description="권한이 부족합니다.", color=0xaa0000)
                await ctx.send(embed=embed)
                return
            if 2 >= check_perm(member):
                embed = discord.Embed(title="Blacklist!", description="봇 관리자의 권한을 가지고 있는 사용자는 블랙리스트에 등재할 수 없습니다.", color=self.color)
                await ctx.send(embed=embed)
                return
            connect = getDatabase()
            cur = connect.cursor()
            sql_Black = "insert into BLACKLIST(ID) value(%s)"
            if 9 == check_perm(member):
                embed = discord.Embed(title="Blacklist!", description=f"{member}는 이미 등재되어 있습니다.",
                                      color=self.color)
                await ctx.send(embed=embed)
                connect.commit()
                connect.close()
                return
            cur.execute(sql_Black, mention)
            connect.commit()
            connect.close()
            embed = discord.Embed(title="Blacklist!", description=f"{member}가 블랙리스트에 추가되었습니다!", color=self.color)
            await ctx.send(embed=embed)
            return
        elif mod == "제거":
            if len(list_message) < 2:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"블랙리스트에 등재할 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            mention = int(list_message[1].replace("<@", "").replace(">", "").replace("!", ""))
            member = await ctx.guild.fetch_member(mention)
            if 2 < check_perm(ctx.author):
                embed = discord.Embed(title="에러", description="권한이 부족합니다.", color=0xaa0000)
                await ctx.send(embed=embed)
                return
            if member is None:
                embed = discord.Embed(title="PUBG BOT 도우미",
                                      description=f"올바른 유저를 기재하여 주세요.",
                                      color=self.color)
                await ctx.send(embed=embed)
                return
            connect = getDatabase()
            cur = connect.cursor()
            sql_delete = "delete from BLACKLIST where ID=%s"
            if 4 >= check_perm(member):
                embed = discord.Embed(title="Blacklist!", description=f"{member}는, 블랙리스트에 추가되어 있지 않습니다.",
                                      color=self.color)
                await ctx.send(embed=embed)
                connect.commit()
                connect.close()
                return
            cur.execute(sql_delete, mention)
            connect.commit()
            connect.close()
            embed = discord.Embed(title="Blacklist!", description=f"{member}가 블랙리스트에서 제거되었습니다!", color=self.color)
            await ctx.send(embed=embed)
            return

    @_command.command(name="서버목록", permission=2, interaction=False)
    async def server_list(self, ctx):
        embed = discord.Embed(title="서버목록", description="서버목록은 개인정보보호를 위해, DM를 통하여 보내드렸습니다.", color=0x00aaaa)
        await ctx.send(embed=embed)
        answer = ""
        total = 0
        for i in range(len(self.client.guilds)):
            if self.client.guilds[i] is None:
                continue
            if (i+1) % 50 == 0:
                await ctx.author.send(f"{answer}\n{(i/50)+1}페이지/{int(len(self.client.guilds)/50)+1}페이지")
                answer = ""
            answer = answer + f"{i + 1}번: {self.client.guilds[i]}({self.client.guilds[i].id}): {self.client.guilds[i].member_count}명\n"
            total += self.client.guilds[i].member_count
        await ctx.author.send(f"{answer}\n방의 종합 멤버:{total}명\n마지막 페이지")
        return

    @_command.command(permission=2, interaction=False)
    async def echo(self, ctx):
        list_message = ctx.options
        prefix = get_prefix(self.client, ctx)
        if len(list_message) < 0:
            embed = discord.Embed(title='PUBG BOT 도우미', description=f'{prefix}echo <내용>\n알맞게 사용해 주시기 바랍니다.',
                                  color=self.color)
            await ctx.send(embed=embed)
            return
        answer = " ".join(list_message[0:])
        await ctx.send(f'{answer}')
        return

    @_command.command(aliases=['리로드'], permission=2, interaction=False)
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
            except commands.ExtensionNotLoaded:
                e_msg += f"\n{ext}를 불러오지 못했습니다."
                err[0] += 1
            except commands.ExtensionNotFound:
                e_msg += f"\n{ext}를 발견하지 못했습니다."
                err[1] += 1
            except commands.ExtensionFailed:
                e_msg += f"\n{ext}에 오류가 발생하였습니다."
                err[2] += 1
        embed = discord.Embed(title="PUBG BOT", description=f"{len(exts)}개의 command가 재로딩 되었습니다.", colour=self.color)
        if not e_msg == "":
            embed.description += f"```에러로그(cog): {e_msg}```"
        await msg.edit(embed=embed)
        return


def setup(client):
    return Command(client)
