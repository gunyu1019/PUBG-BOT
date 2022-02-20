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
import datetime

import discord
import asyncio
import pymysql
from typing import Optional, NamedTuple

from config.config import parser
from discord.ext import interaction
from discord.ext.interaction import ApplicationContext, ComponentsContext, ActionRow, Button
from module import pubgpy
from utils.database import get_database

xbox = discord.PartialEmoji(name="XBOX", id=718482204035907586)
playstation = discord.PartialEmoji(name="PS", id=718482204417720400)
steam = discord.PartialEmoji(name="Steam", id=698454004656504852)
kakao = discord.PartialEmoji(name="kakao", id=718482204103278622)
stadia = discord.PartialEmoji(name="Stadia", id=718482205575348264)

game_ids = ["steam", "kakao", "xbox", "psn", "stadia"]
game_enums = [
    pubgpy.Platforms.STEAM,
    pubgpy.Platforms.KAKAO,
    pubgpy.Platforms.XBOX,
    pubgpy.Platforms.PLAYSTATION,
    pubgpy.Platforms.STADIA,
]

color = int(parser.get("Color", "default"), 16)
error_color = int(parser.get("Color", "error"), 16)
warning_color = int(parser.get("Color", "warning"), 16)


class Player(NamedTuple):
    id: str
    platform: pubgpy.Platforms
    message: Optional[interaction.Message] = None


class PlatformSelection(NamedTuple):
    player: Player
    platform_id: int


async def player_info(
        nickname: str,
        ctx: ApplicationContext,
        client: discord.Client,
        pubg_client: pubgpy.Client
) -> Optional[Player]:
    connect = await get_database()
    player_data = await connect.query(
        table="player_data",
        key_name="nickname",
        key=nickname,
        filter_col=["player_id", "platform"]
    )
    if player_data is None:
        _player_platform = await player_platform(nickname, ctx, client, pubg_client)
        if _player_platform is None:
            await connect.close()
            return None

        result = await connect.is_exist(
            table="player_data",
            key_name="player_id",
            key=_player_platform.player.id
        )
        if not result:
            await connect.insert(
                table="player_data",
                value={
                    "nickname": nickname,
                    "platform": int(_player_platform.platform_id),
                    "player_id": _player_platform.player.id
                }
            )
        else:
            await connect.update(
                table="player_data",
                key_name="player_id",
                key=_player_platform.player.id,
                value={
                    "nickname": nickname,
                    "platform": int(_player_platform.platform_id)
                }
            )
        await connect.close(check_commit=True)
        return _player_platform.player
    else:
        player_id = player_data['player_id']
        platform = game_enums[player_data['platform']]
    await connect.close()
    return Player(player_id, platform)


async def player_platform(
        nickname: str,
        ctx: ApplicationContext,
        client: interaction.Client,
        pubg_client: pubgpy.Client
) -> Optional[PlatformSelection]:
    embed = discord.Embed(
        title="플랫폼 선택!",
        description="해당 계정의 플랫폼을 선택해주세요.\n초기에 한번만 눌러주시면 됩니다.",
        color=color
    )
    components = [
        ActionRow(components=[
            Button(
                custom_id="0",
                style=2,
                emoji=steam
            ),
            Button(
                custom_id="1",
                style=2,
                emoji=kakao
            ),
            Button(
                custom_id="2",
                style=2,
                emoji=xbox
            ),
            Button(
                custom_id="3",
                style=2,
                emoji=playstation
            ),
            Button(
                custom_id="4",
                style=2,
                emoji=stadia
            )
        ])
    ]
    msg = await ctx.send(embed=embed, components=components)

    def check(component: ComponentsContext):
        return component.component_type == 2 and msg.id == component.message.id and ctx.author == component.author

    try:
        result: ComponentsContext = await client.wait_for_global_component(check=check, timeout=300)
    except asyncio.TimeoutError:
        return None
    new_platform = game_ids[int(result.custom_id)]
    embed = discord.Embed(
        title="플랫폼 선택!",
        description="{}가 선택되었습니다.\n값이 잘못되었을 경우 `플랫폼변경` 명령어를 사용해주세요.".format(new_platform),
        color=color
    )
    for x in msg.components:
        x.disabled = True

    try:
        await result.update(embed=embed, components=msg.components)
    except discord.NotFound:
        await msg.edit(embed=embed, components=[])
    platform_data = pubgpy.get_enum(pubgpy.Platforms, new_platform)
    if platform_data is None or platform_data == new_platform:
        embed = discord.Embed(
            title="에러",
            description="플랫폼 정보가 잘못되었습니다. 관리자에게 문의해주시기 바랍니다.",
            color=error_color
        )
        await msg.edit(embed=embed)
        return None
    pubg_client.platform(platform_data)
    for i in range(5):
        try:
            player: pubgpy.Player = await pubg_client.player(nickname=nickname)
        except pubgpy.NotFound:
            embed = discord.Embed(
                title="에러",
                description="사용자를 찾을 수 없습니다. 닉네임을 확인해주세요.",
                color=error_color
            )
            await msg.edit(embed=embed)
            return None
        except pubgpy.TooManyRequests as error:
            timer = (error.reset - datetime.datetime.now()).total_seconds()
            if timer < 0:
                continue
            v = int(timer / 5)
            if timer % 5 >= 1:
                v += 1

            for count in range(v):
                embed = discord.Embed(
                    title="대기열",
                    description="너무 많은 요청으로 처리가 지연되고 있습니다. {0}초 후 다시 시도합니다.".format((v - count) * 5),
                    color=warning_color
                )
                if i >= 1:
                    embed.description += " (재시도: {0}/5회)".format(i+1)
                await msg.edit(embed=embed)
                await asyncio.sleep(5)
        else:
            break
    else:
        embed = discord.Embed(
            title="에러",
            description="너무 많은 요청으로 처리가 지연되고 있습니다. 잠시 후 다시 시도해주세요.",
            color=error_color
        )
        await msg.edit(embed=embed)
        return None
    player_id = player.id
    platform = platform_data

    return PlatformSelection(
        Player(player_id, platform, msg),
        result.custom_id
    )
