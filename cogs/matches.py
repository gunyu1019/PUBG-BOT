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

from discord.ext import interaction
from discord.ext import commands

from config.config import parser
from module import pubgpy
from module.message import MessageCommand
from process import player
from process.matches import Match
from utils import token
from utils.permission import permission, permission_cog


class Matches:
    def __init__(self, bot: interaction.Client):
        self.client = bot

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=token.PUBG_API)

    async def _option_error(self, ctx, message):
        embed = discord.Embed(
            title="오류",
            description="{message}".format(message=message),
            color=self.warning_color
        )
        await ctx.send(embed=embed)
        return

    def cog_check(self, _):
        return True

    async def cog_before_invoke(self, ctx):
        pass

    async def cog_after_invoke(self, ctx):
        pass

    async def cog_command_error(self, ctx, error):
        pass

    @commands.command(name="매치")
    @permission_cog(4)
    async def match_command(self, ctx):
        convert_context = MessageCommand(ctx.message, self.client)
        if convert_context.name is None or ctx.guild.id != 589033421121126400:  # Only Official PUBG Community in Korea
            return
        convert_context.name = self.match_command.name
        convert_context.prefix = ctx.prefix
        usage_command = "`사용법: {prefix}매치 <닉네임>`".format(prefix=convert_context.prefix)
        if len(convert_context.options) <= 0:
            await self._option_error(ctx, "닉네임을 입력해주세요.\n{0}".format(usage_command))
            return
        if len(convert_context.options) > 1:
            await self._option_error(ctx, "올바른 사용방법이 아닙니다. 닉네임만 작성해주세요.\n{0}".format(usage_command))
            return
        await self.match(convert_context, *convert_context.options)
        return

    @interaction.context(name='매치')
    @permission(4)
    async def match_context(self, ctx):
        message = ctx.target(target_type="message")
        if message.content is None:
            await self._option_error(ctx, "닉네임을 찾을 수 없습니다.")
            return
        option1 = message.content
        if len(option1.split()) > 1:
            await self._option_error(ctx, "올바른 사용방법이 아닙니다. 닉네임만 작성해주세요.")
            return
        await self.match(ctx, option1)
        return

    @interaction.command(name="매치", description='검색된 사용자의 플레이 내역를 불러옵니다.')
    @interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.')
    @interaction.option(
        name='매치_순서',
        description='검색된 플레이 내역의 매치 번호입니다. 최근에 플레이 한 매치를 시작으로 순서대로 1부터 나열됩니다.',
        min_value=1
    )
    @interaction.option(name='업데이트', description='플레이어의 플레이 내역을 업데이트 합니다.')
    @permission(4)
    async def match(self, ctx, option1: str, option2: int = None, option3: bool = False):
        await ctx.defer()
        player_info = await player.player_info(option1, ctx, self.client, self.pubgpy)
        if player_info is None:
            return
        match = Match(
                ctx=ctx,
                client=self.client,
                pubg=self.pubgpy,
                player_id=player_info.id,
                player=option1
        )
        self.pubgpy.platform(player_info.platform)

        if option3:
            await match.database2.update_matches(player_id=player_info.id)

        msg = None
        if option2 is None:
            msg, option2 = await match.choice_match()
            if msg is None:
                return
        match_list = await match.database2.get_matches_lists(player_id=player_info.id)
        if len(match_list) < option2:
            await self._option_error(
                ctx, "해당 순서의 매치를 찾을 수 없습니다. (발견된 매치 갯수: {})".format(len(match_list))
            )
            return
        elif 0 > option2:
            await self._option_error(
                ctx, "매치 순서값으로 음수 값을 줄 수 없습니다."
            )
            return
        await match.match_stats(match_list[option2], msg)
        return


def setup(client):
    return client.add_icog(Matches(client))
