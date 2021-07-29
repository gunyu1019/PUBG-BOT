import discord
import json

from typing import Union, Optional, Tuple, List

import pymysql.cursors

from module import commands
from module import pubgpy
from module.interaction import SlashContext, Message
from process import player
from utils import token
from utils.database import getDatabase
from process.status import Status


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619
        self.pubgpy = pubgpy.Client(token=token.PUBG_API)

    @staticmethod
    def _choose_to_option1(ranked: bool = True) -> Tuple[List[str], List[str]]:
        all_option = ["1인칭", "3인칭", "일반", "3인칭경쟁", "경쟁", "랭크", "1인칭경쟁"]
        all_option_comment = ["1인칭", "3인칭, 일반", "3인칭경, 경쟁, 랭크", "1인칭경쟁"]
        return (all_option, all_option_comment) if ranked else (all_option[0:3], all_option_comment[0:1])

    async def _option_error(self, ctx, message):
        embed = discord.Embed(
            title="에러",
            description="{message}".format(message=message),
            color=self.color
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="전적", aliases=["전적솔로", "전적듀오", "전적스쿼드"], permission=4)
    async def status(self, ctx: Union[SlashContext, Message]):
        if ctx.name == "전적듀오":
            all_option, all_option_comment = self._choose_to_option1(ranked=False)
        else:
            all_option, all_option_comment = self._choose_to_option1()
        command = "{prefix}{command_name} <{comment}> <닉네임> <시즌(선택)>".format(
            command_name=ctx.name, prefix=ctx.prefix, comment="|".join(all_option_comment))
        option1 = None
        option2 = None
        option3 = None
        if isinstance(ctx, Message):
            options = ctx.options
            if len(options) < 1:
                await self._option_error(
                    ctx, "**{}**\n {} 중에서만 선택하여 주세요.".format(command, ", ".join(all_option_comment))
                )
                return
            tp = options[0]
            if tp not in all_option:
                await self._option_error(
                    ctx, "**{}**\n {} 중에서만 선택하여 주세요.".format(command, ", ".join(all_option_comment))
                )
                return
            if tp == "1인칭":
                option1 = 0
            elif tp == "3인칭" or tp == "일반":
                option1 = 1
            elif tp == "1인칭경쟁":
                option1 = 2
            elif tp == "3인칭경쟁" or tp == "경쟁" or tp == "랭크":
                option1 = 3
            else:
                await self._option_error(
                    ctx, "**{}**\n {} 중에서만 선택하여 주세요.".format(command, ", ".join(all_option_comment))
                )
                return

            if len(options) < 2:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
            option2 = options[1]
            option3 = options[2] if len(options) > 2 else None
        elif isinstance(ctx, SlashContext):
            options = ctx.options
            option1 = options.get("유형")
            if option1 is None or 0 > options.get("유형", -1) or options.get("유형", 5) > 4:
                await self._option_error(
                    ctx, "**{}**\n {} 중에서만 선택하여 주세요.".format(command, ", ".join(all_option_comment))
                )
                return

            option2: Optional[str] = options.get("닉네임")
            if option2 is None:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return

            option3 = options.get("시즌")
        player_id, _platform = await player.player_info(option2, ctx, self.client, self.pubgpy)
        if player_id is None:
            return

        if option3 is not None:
            season = pubgpy.get_season(int(option3), _platform)
        else:
            connect = getDatabase()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM SEASON_STATUS"
            cur.execute(sql)
            season_data = cur.fetchone()
            database_platform = {"steam": "Steam", "kakao": "Kakao", "xbox": "XBOX", "psn": "PSN", "stadia": "Stadia"}
            connect.close()

            season = json.loads(season_data.get(database_platform[_platform.value], {})).get("data", [{}])[-1].get("id")

        self.pubgpy.platform(_platform)
        status = Status(
                ctx=ctx,
                client=self.client,
                pubg=self.pubgpy,
                player_id=player_id,
                player=option2,
                season=season
        )
        if ctx.name == "전적솔로":
            if option1 == 0:
                await status.normal_mode(mode="solo_fpp")
            elif option1 == 1:
                await status.normal_mode(mode="solo")
            elif option1 == 2:
                await status.ranked_mode(mode="solo_fpp")
            elif option1 == 3:
                await status.ranked_mode(mode="solo")
        elif ctx.name == "전적듀오":
            if option1 == 0:
                await status.normal_mode(mode="duo_fpp")
            elif option1 == 1:
                await status.normal_mode(mode="duo")
            elif option1 == 2 or option1 == 3:
                await self._option_error(ctx, "**{}**\n 경쟁전에서는 듀오모드를 지원하지 않습니다.".format(command))
        elif ctx.name == "전적스쿼드":
            if option1 == 0:
                await status.normal_mode(mode="squad_fpp")
            elif option1 == 1:
                await status.normal_mode(mode="squad")
            elif option1 == 2:
                await status.ranked_mode(mode="squad_fpp")
            elif option1 == 3:
                await status.ranked_mode(mode="squad")
        else:
            if option1 == 0:
                await status.normal_total(fpp=True)
            elif option1 == 1:
                await status.normal_total()
            elif option1 == 2:
                await status.ranked_total(fpp=True)
            elif option1 == 3:
                await status.ranked_total()
        return

    @commands.command(name="플랫폼변경", permission=4)
    async def platform_change(self, ctx):
        connect = getDatabase()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        command = "{prefix}{command_name} <닉네임>".format(command_name=ctx.name, prefix=ctx.prefix)
        nickname = None
        if isinstance(ctx, Message):
            options = ctx.options

            if len(options) < 1:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
            nickname = options[0]
        elif isinstance(ctx, SlashContext):
            options = ctx.options
            nickname: Optional[str] = options.get("닉네임")
            if nickname is None:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
        player_id, _, platform_id = await player.player_platform(nickname, ctx, self.client, self.pubgpy)
        if player_id is None:
            connect.close()
            return

        sql = pymysql.escape_string(
            "UPDATE player_data SET platform=%s WHERE player_id=%s and nickname=%s"
        )
        cur.execute(sql, (int(platform_id), player_id, nickname))
        connect.commit()
        connect.close()
        return

def setup(client):
    return Command(client)
