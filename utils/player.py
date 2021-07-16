import discord
import pymysql

from module.pubgpy import Client
from module.interaction import SlashContext, Message
from module.components import ActionRow, Button
from utils.database import getDatabase
from utils.token import token
from typing import Union

xbox = discord.PartialEmoji(name="XBOX", id=718482204035907586)
playstation = discord.PartialEmoji(name="PS", id=718482204417720400)
steam = discord.PartialEmoji(name="Steam", id=698454004656504852)
kakao = discord.PartialEmoji(name="kakao", id=718482204103278622)
stadia = discord.PartialEmoji(name="Stadia", id=718482205575348264)


async def player_info(
        nickname: str,
        ctx: Union[SlashContext, Message],
        client: discord.Client
):
    connect = getDatabase()
    cur = connect.cursor()

    sql = pymysql.escape_string("select id,platform from player where name=%s")
    cur.execute(sql, nickname)
    player_data = cur.fetchone()
    if player_data is None:
        embed = discord.Embed(title="플랫폼 선택!", description="해당 계정의 플랫폼을 선택해주세요.\n초기에 한번만 눌러주시면 됩니다.", color=0xffd619)
        components = [
            ActionRow(components=[
                Button(
                    custom_id="steam",
                    style=2,
                    emoji=steam
                ),
                Button(
                    custom_id="kakao",
                    style=2,
                    emoji=kakao
                ),
                Button(
                    custom_id="xbox",
                    style=2,
                    emoji=xbox
                ),
                Button(
                    custom_id="playstation",
                    style=2,
                    emoji=playstation
                ),
                Button(
                    custom_id="stadia",
                    style=2,
                    emoji=stadia
                )
            ])
        ]
        msg = await ctx.send(embed=embed, components=components)

        def check(result):
            return True
        result = await client.wait_for("components", check=check)
    return