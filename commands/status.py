import discord

from typing import Union, Optional

import pymysql.cursors

from module import commands
from module import pubgpy
from module.interaction import SlashContext, Message
from utils import player
from utils import token
from utils.database import getDatabase


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619
        self.pubgpy = pubgpy.Client(token=token.PUBG_API)

    async def option1_error(self, ctx, message):
        embed = discord.Embed(
            title="에러",
            description="{message}".format(message=message),
            color=self.color
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="전적", permission=4)
    async def status(self, ctx: Union[SlashContext, Message]):
        command = "{prefix}전적 <1인칭|3인칭, 일반|3인칭경쟁, 경쟁, 랭크|1인칭경쟁> <닉네임> <시즌(선택)>".format(prefix=ctx.prefix)
        all_option = ["1인칭", "3인칭", "일반", "3인칭경쟁", "경쟁", "랭크", "1인칭경쟁"]
        option1 = None
        option2 = None
        option3 = None
        if isinstance(ctx, Message):
            options = ctx.options
            if len(options) < 1:
                await self.option1_error(ctx, "**{}**\n 1인칭, 3인칭 혹은 일반, 랭크 중에서만 선택하여 주세요.".format(command))
                return
            tp = options[0]
            if tp not in all_option:
                await self.option1_error(ctx, "**{}**\n 1인칭, 3인칭 혹은 일반, 랭크 중에서만 선택하여 주세요.".format(command))
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
                await self.option1_error(ctx, "**{}**\n 1인칭, 3인칭 혹은 일반, 랭크 중에서만 선택하여 주세요.".format(command))
                return

            if len(options) < 2:
                await self.option1_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
            option2 = options[1]
            option3 = options[2] if len(options) > 2 else None
        elif isinstance(ctx, SlashContext):
            options = ctx.options
            option1 = options.get("유형")
            if option1 is None or 0 > options.get("유형", -1) or options.get("유형", 5) > 4:
                await self.option1_error(ctx, "**{}**\n 1인칭, 3인칭 혹은 일반, 랭크 중에서만 선택하여 주세요.".format(command))
                return

            option2: Optional[str] = options.get("닉네임")
            if option2 is None:
                await self.option1_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
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

            season = season_data.get(database_platform[_platform.value], {}).get("data", [{}])[-1].get("id")
        return


def setup(client):
    return Command(client)
