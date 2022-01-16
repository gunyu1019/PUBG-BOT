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

import discord
import json

from typing import Optional, Tuple, List
from discord.ext import interaction

import pymysql.cursors

from config.config import parser
from module import pubgpy
from process import player
from utils import token
from utils.database import get_database
from utils.permission import permission
from process.status import Status as ProcessStatus


class Status:
    def __init__(self, bot):
        self.client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=token.PUBG_API)

    @staticmethod
    def _choose_to_option1(ranked: bool = True) -> Tuple[List[str], List[str]]:
        all_option = ["1인칭", "3인칭", "일반", "3인칭경쟁", "경쟁", "랭크", "1인칭경쟁"]
        all_option_comment = ["1인칭", "3인칭, 일반", "3인칭경쟁, 경쟁, 랭크", "1인칭경쟁"]
        return (all_option, all_option_comment) if ranked else (all_option[0:3], all_option_comment[0:1])

    async def _option_error(self, ctx, message):
        embed = discord.Embed(
            title="에러",
            description="{message}".format(message=message),
            color=self.warning_color
        )
        await ctx.send(embed=embed)
        return

    @interaction.command(name="전적솔로", description='검색된 사용자의 솔로 전적 정보를 불러옵니다.')
    @interaction.option(name='유형', description='1인칭/3인칭과 일반게임/경쟁전을 구분합니다.', choices=[
        interaction.CommandOptionChoice(name='일반(1인칭)', value=0),
        interaction.CommandOptionChoice(name='일반(3인칭)', value=1),
        interaction.CommandOptionChoice(name='랭크(1인칭)', value=2),
        interaction.CommandOptionChoice(name='랭크(3인칭)', value=3)
    ], min_value=0, max_value=3)
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @interaction.option(name='시즌', description='조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.', min_value=1)
    @permission(4)
    async def status_solo(self, ctx, option1: int, option2: str, option3: int = None):
        await self.status(ctx, option1, option2, option3)
        return

    @interaction.command(name="전적듀오", description='검색된 사용자의 듀오 전적 정보를 불러옵니다.')
    @interaction.option(name='유형', description='1인칭/3인칭과 일반게임/경쟁전을 구분합니다.', choices=[
        interaction.CommandOptionChoice(name='일반(1인칭)', value=0),
        interaction.CommandOptionChoice(name='일반(3인칭)', value=1)
    ], min_value=0, max_value=1)
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @interaction.option(name='시즌', description='조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.', min_value=1)
    @permission(4)
    async def status_duo(self, ctx, option1: int, option2: str, option3: int = None):
        await self.status(ctx, option1, option2, option3)
        return

    @interaction.command(name="전적스쿼드", description='검색된 사용자의 스쿼드 전적 정보를 불러옵니다.')
    @interaction.option(name='유형', description='1인칭/3인칭과 일반게임/경쟁전을 구분합니다.', choices=[
        interaction.CommandOptionChoice(name='일반(1인칭)', value=0),
        interaction.CommandOptionChoice(name='일반(3인칭)', value=1),
        interaction.CommandOptionChoice(name='랭크(1인칭)', value=2),
        interaction.CommandOptionChoice(name='랭크(3인칭)', value=3)
    ], min_value=0, max_value=3)
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @interaction.option(name='시즌', description='조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.', min_value=1)
    @permission(4)
    async def status_squad(self, ctx, option1: int, option2: str, option3: int = None):
        await self.status(ctx, option1, option2, option3)
        return

    @interaction.context(name='전적솔로')
    async def status_context_solo(self, ctx):
        return self.status_context(ctx)

    @interaction.context(name='전적듀오')
    async def status_context_duo(self, ctx):
        return self.status_context(ctx)

    @interaction.context(name='전적스쿼드')
    @permission(4)
    async def status_context_squad(self, ctx):
        return self.status_context(ctx)

    @interaction.context(name='전적')
    @permission(4)
    async def status_context(self, ctx):
        all_option, all_option_comment = self._choose_to_option1()
        message = ctx.target(target_type="message")
        if message.content is None:
            await self._option_error(ctx, "명령어를 실행하기 위한 닉네임/유형을 찾을 수 없습니다.")
            return
        options = message.content.split()
        option1 = None
        option2 = None

        if len(options) > 2 or len(options) == 0:
            await self._option_error(
                ctx,
                "유형 선택이 잘못되었습니다. {0} 내에서 만 선택해제세요"
                "<유형(선택)> <닉네임> 또는 닉네임만 작성해주세요.".format(", ".join(all_option_comment))
            )
            return
        elif len(options) == 2:
            _option1 = options[0]
            if _option1 not in all_option:
                await self._option_error(
                    ctx,
                    "올바른 사용방법이 아닙니다. <유형(선택)> <닉네임>과 같이 작성해주세요. (ex. \"경쟁 kimblue\")\n"
                    "또는 닉네임만 작성해주세요. 이 경우 유형은 일반으로 자동 선택됩니다."
                )
            if _option1 == "1인칭":
                option1 = 0
            elif _option1 == "3인칭" or _option1 == "일반":
                option1 = 1
            elif _option1 == "1인칭경쟁":
                option1 = 2
            elif _option1 == "3인칭경쟁" or _option1 == "경쟁" or _option1 == "랭크":
                option1 = 3
            option2: Optional[str] = options[1]
        elif len(options) == 1:
            option1 = 1
            option2: Optional[str] = options[0]
        await self.status(ctx, option1, option2)
        return

    @interaction.command(name="전적", description='검색된 사용자의 전적 정보를 불러옵니다.')
    @interaction.option(name='유형', description='1인칭/3인칭과 일반게임/경쟁전을 구분합니다.', choices=[
        interaction.CommandOptionChoice(name='일반(1인칭)', value=0),
        interaction.CommandOptionChoice(name='일반(3인칭)', value=1),
        interaction.CommandOptionChoice(name='랭크(1인칭)', value=2),
        interaction.CommandOptionChoice(name='랭크(3인칭)', value=3)
    ], min_value=0, max_value=3)
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @interaction.option(name='시즌', description='조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.', min_value=1)
    @permission(4)
    async def status(self, ctx: interaction.ApplicationContext, option1: int, option2: str, option3: int = None):
        if ctx.name == "전적듀오":
            all_option, all_option_comment = self._choose_to_option1(ranked=False)
        else:
            all_option, all_option_comment = self._choose_to_option1()
        command = "/{command_name} <{comment}> <닉네임> <시즌(선택)>".format(
            command_name=ctx.name, comment="|".join(all_option_comment)
        )

        if option1 is None or 0 > option1 or option1 > 4:
            await self._option_error(
                ctx, "**{}**\n {} 중에서만 선택하여 주세요.".format(command, ", ".join(all_option_comment))
            )
            return
        if option2 is None:
            await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
            return

        await ctx.defer()
        player_id, _platform = await player.player_info(option2, ctx, self.client, self.pubgpy)
        if player_id is None:
            return

        season = None
        if option3 is not None:
            season = pubgpy.get_season(option3, _platform)
        else:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM SEASON_STATUS"
            cur.execute(sql)
            season_data = cur.fetchone()
            database_platform = {"steam": "Steam", "kakao": "Kakao", "xbox": "XBOX", "psn": "PSN", "stadia": "Stadia"}
            connect.close()

            seasons = json.loads(season_data.get(database_platform[_platform.value], {}))
            for s in seasons.get("data", []):
                if s.get("attributes", {}).get("isCurrentSeason"):
                    season = s.get("id")

        self.pubgpy.platform(_platform)
        status = ProcessStatus(
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

    @interaction.command(name="플랫폼변경", description='등록된 유저의 플랫폼을 잘못 등록할 경우에 사용하는 기능입니다. 명령어를 이용하여 등록된 사용자의 플랫폼을 변경합니다.')
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @permission(4)
    async def platform_change(self, ctx, nickname: str):
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if ctx.application_type == 1:
            options = ctx.options
            nickname: str = options.get("닉네임")
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
    return client.add_icog(Status(client))
