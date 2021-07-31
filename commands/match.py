import discord
import json

from typing import Union, Optional, Tuple, List

from module import commands
from module import pubgpy
from module.interaction import SlashContext, Message
from process import player
from process.match import Match
from utils import token


class Command:
    def __init__(self, bot):
        self.client = bot
        self.color = 0xffd619
        self.pubgpy = pubgpy.Client(token=token.PUBG_API)

    async def _option_error(self, ctx, message):
        embed = discord.Embed(
            title="에러",
            description="{message}".format(message=message),
            color=self.color
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="매치", permission=4)
    async def match(self, ctx):
        command = "{prefix}{command_name} <닉네임>".format(command_name=ctx.name, prefix=ctx.prefix)
        option1 = None
        option2 = None
        option3 = False
        if isinstance(ctx, Message):
            options = ctx.options

            if len(options) < 1:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
            option1 = options[0]
            option2 = options[1] if len(options) > 2 else None
        elif isinstance(ctx, SlashContext):
            options = ctx.options
            option1: Optional[str] = options.get("닉네임")
            if option1 is None:
                await self._option_error(ctx, "**{}**\n 닉네임을 작성하여 주세요.".format(command))
                return
            option2 = options.get("매치_순서")
            option3 = options.get("업데이트", False)
        player_id, _platform = await player.player_info(option1, ctx, self.client, self.pubgpy)
        if player_id is None:
            return
        match = Match(
                ctx=ctx,
                client=self.client,
                pubg=self.pubgpy,
                player_id=player_id,
                player=option1
        )
        self.pubgpy.platform(_platform)

        if option3:
            await match.database2.update_matches(player_id=player_id)

        msg = None
        if option2 is None:
            msg, option2 = await match.choice_match()
        match_list = match.database2.get_matches_lists(player_id=player_id)
        if len(match_list) < option2:
            await self._option_error(
                ctx, "**{}**\n 해당 순서의 매치를 찾을 수 없습니다. (발견된 매치 갯수: {})".format(command, len(match_list))
            )
            return
        await match.match_stats(match_list[option2], msg)
        return


def setup(client):
    return Command(client)
