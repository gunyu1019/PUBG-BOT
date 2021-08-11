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
from config.config import parser
from utils.directory import directory


async def forbidden_manage(ctx):
    embed_warning = discord.Embed(
        title="\U000026A0 경고!",
        description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.",
        color=0xffd619
    )
    file_warning = discord.File(f"{directory}/assets/manage_message.png")
    embed_warning.set_image(url="attachment://manage_message.png")
    embed_warning.add_field(
        name="Q: 왜 `메세지 관리`가 필요한가요?",
        value="A: 선택형을 해야하는 메세지(동적 메세지)는 메세지 꼬임 방지를 위하여, 모든 반응을 삭제해야하도록 만들었습니다. 그러나 모든 반응을 삭제하기 위해서는 `메세지 관리` 권한이 "
              "필요합니다.",
        inline=True)
    await ctx.send(embed=embed_warning, file=file_warning)
    return


async def inspection(ctx):
    embed = discord.Embed(
        title="\U000026A0 안내",
        description=f"죄송합니다. 지금은 PUBG BOT 점검 중입니다. 잠시 후 다시 시도해주세요. :(",
        color=0xffd619
    )

    if parser.get("Inspection", "reason") != "" and parser.get("Inspection", "reason") is not None:
        embed.description += "\n{}".format(parser.get("Inspection", "reason"))

    if parser.get("Inspection", "date") != "" and parser.get("Inspection", "date") is not None:
        embed.description += "\n\n기간: {}".format(parser.get("Inspection", "date"))
    await ctx.send(embed=embed)
    return
