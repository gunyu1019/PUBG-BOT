import discord
import pymysql
import json

from module.interaction import SlashContext, ComponentsContext
from module.message import Message
from module.components import ActionRow, Button
from module import pubgpy
from utils.database import getDatabase
from utils.directory import directory
from typing import Union

xbox = discord.PartialEmoji(name="XBOX", id=718482204035907586)
playstation = discord.PartialEmoji(name="PS", id=718482204417720400)
steam = discord.PartialEmoji(name="Steam", id=698454004656504852)
kakao = discord.PartialEmoji(name="kakao", id=718482204103278622)
stadia = discord.PartialEmoji(name="Stadia", id=718482205575348264)

game_ids = ["steam", "kakao", "xbox", "psn", "stadia"]


async def player_info(
        nickname: str,
        ctx: Union[SlashContext, Message],
        client: discord.Client,
        pubg_client: pubgpy.Client
):
    connect = getDatabase()
    cur = connect.cursor(pymysql.cursors.DictCursor)

    sql = pymysql.escape_string("select id, platform from player where name=%s")
    cur.execute(sql, nickname)
    player_data = cur.fetchone()
    if player_data is None:
        player_id, platform, platform_id = await player_platform(nickname, ctx, client, pubg_client)
        if player_id is None:
            connect.close()
            return None, None

        sql = pymysql.escape_string("insert into player(id,name,last_update,platform) values (%s, %s, %s, %s)")
        with open("{}/data/player_sample_data.json".format(directory)) as f:
            sample = json.load(f)
        cur.execute(sql, (player_id, nickname, json.dumps(sample), int(platform_id)))
        connect.commit()
    else:
        player_id = player_data['id']
        platform = game_ids[player_data['platform']]
    connect.close()
    return player_id, platform


async def player_platform(
        nickname: str,
        ctx: Union[SlashContext, Message],
        client: discord.Client,
        pubg_client: pubgpy.Client
):
    embed = discord.Embed(
        title="플랫폼 선택!",
        description="해당 계정의 플랫폼을 선택해주세요.\n초기에 한번만 눌러주시면 됩니다.",
        color=0xffd619
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
        if component.component_type == 2 and msg.id == component.message.id and ctx.author == component.author:
            return component.message.webhook_id

    result: ComponentsContext = await client.wait_for("components", check=check)
    new_platform = game_ids[int(result.custom_id)]
    embed = discord.Embed(
        title="플랫폼 선택!",
        description="{}가 선택되었습니다.\n값이 잘못되었을 경우 `플랫폼변경` 명령어를 사용해주세요.".format(new_platform),
        color=0xffd619
    )
    await result.update(embed=embed, components=[])
    platform_data = pubgpy.get_enum(pubgpy.Platforms, new_platform)
    if platform_data is None or platform_data == new_platform:
        embed = discord.Embed(
            title="에러",
            description="플랫폼 정보가 잘못되었습니다. 관리자에게 문의해주시기 바랍니다.",
            color=0xffd619
        )
        await ctx.edit(embed=embed)
        return None, None, None
    pubg_client.platform(platform_data)
    try:
        player: pubgpy.Player = await pubg_client.player(nickname=nickname)
    except pubgpy.NotFound:
        embed = discord.Embed(
            title="에러",
            description="사용자를 찾을 수 없습니다. 닉네임을 확인해주세요.",
            color=0xffd619
        )
        await ctx.edit(embed=embed)
        return None, None, None
    except pubgpy.TooManyRequests:
        embed = discord.Embed(
            title="에러",
            description="너무 많은 요청으로 처리가 지연되고 있습니다. 잠시 후 다시 시도해주세요.",
            color=0xffd619
        )
        await ctx.edit(embed=embed)
        return None, None, None
    player_id = player.id
    platform = platform_data

    return player_id, platform, result.custom_id
