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
import asyncio
import discord
import datetime

from discord.ext import interaction
from typing import Coroutine, Any, Callable, TypeVar, Optional
from pytz import timezone

from config.config import get_config
from module import pubgpy
from utils.location import comment

T = TypeVar("T")

parser = get_config()

color = int(parser.get("Color", "default"), 16)
error_color = int(parser.get("Color", "error"), 16)
warning_color = int(parser.get("Color", "warning"), 16)


async def request_loop(
    context: interaction.ApplicationContext,
    call: Callable[..., Coroutine[Any, Any, T]],
    maximum_loop: int = 5,
    language: str = None,
    *args,
    **kwargs,
) -> Optional[T]:
    if language is None:
        language = context.locale

    for index in range(maximum_loop):
        try:
            result = await call(*args, **kwargs)
            break
        except pubgpy.TooManyRequests as error:
            timer = (
                error.reset
                - datetime.datetime.now(tz=timezone("Asia/Seoul")).replace(tzinfo=None)
            ).total_seconds()
            if timer < 0:
                continue
            v = int(timer / 5)
            if timer % 5 >= 1:
                v += 1

            for count in range(v):
                embed = discord.Embed(
                    title=comment("request_loop", "wait_list_title", language),
                    description=comment(
                        "request_loop", "wait_list_description", language
                    ).format((v - count) * 5),
                    color=warning_color,
                )
                if index >= 1:
                    embed.description += " (재시도: {0}/5회)".format(index + 1)
                await context.edit(embed=embed)
                await asyncio.sleep(5)
    else:
        embed = discord.Embed(
            title=comment("basic", "error", language),
            description=comment("request_loop", "wait_list_failed", language),
            color=error_color,
        )
        await context.edit(embed=embed)
        return None
    return result
