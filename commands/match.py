import discord
import json

from typing import Union, Optional, Tuple, List

from module import commands
from module import pubgpy
from module.interaction import SlashContext, Message
from process import player
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
        player_id, _platform = await player.player_info(option1, ctx, self.client, self.pubgpy)
        if player_id is None:
            return

        self.pubgpy.platform(_platform)
        return


def setup(client):
    return Command(client)
