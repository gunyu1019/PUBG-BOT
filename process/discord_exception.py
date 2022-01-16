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

import discord
from config.config import parser

color = int(parser.get("Color", "default"), 16)
error_color = int(parser.get("Color", "error"), 16)
warning_color = int(parser.get("Color", "warning"), 16)


async def inspection(ctx):
    embed = discord.Embed(
        title="\U000026A0 안내",
        description="죄송합니다. 지금은 PUBG BOT 점검 중입니다. 잠시 후 다시 시도해주세요. :(",
        color=warning_color
    )

    if parser.get("Inspection", "reason") != "" and parser.get("Inspection", "reason") is not None:
        embed.description += "\n{}".format(parser.get("Inspection", "reason"))

    if parser.get("Inspection", "date") != "" and parser.get("Inspection", "date") is not None:
        embed.description += "\n\n기간: {}".format(parser.get("Inspection", "date"))
    await ctx.send(embed=embed)
    return
