import discord
import json

from datetime import datetime
from typing import Union
from pytz import timezone
from module import pubgpy
from module.components import ActionRow, Button, Selection
from module.interaction import SlashContext, Message, ComponentsContext
from utils.cache import CacheMatches, CacheMatchesList
from utils.directory import directory
from utils.time import get_time_to_string

with open(f"{directory}/data/deathReason.json", "r", encoding='utf-8') as f:
    death_reason = json.load(f)
with open(f"{directory}/data/mapName.json", "r", encoding='utf-8') as f:
    map_id = json.load(f)


class Match:
    def __init__(
            self,
            ctx: Union[SlashContext, Message],
            client: discord.Client,
            pubg: pubgpy.Client,
            player: str,
            player_id: str,
    ):
        self.ctx = ctx
        self.client = client
        self.pubg = pubg
        self.database1 = CacheMatches(self.pubg)
        self.database2 = CacheMatchesList(self.pubg)
        self.player_nickname = player
        self.player_id = player_id
        self.player = self.pubg.player_id(self.player_id)

        self.default_map_size = 102000

    @staticmethod
    def check(ctx: Message, tp: Union[Button, Selection]):
        def check_func(component: ComponentsContext):
            return component.component_type == tp.type and ctx.id == component.message.id
        return check_func

    async def choice_match(self, b_msg: Message = None):
        matches = await self.database2.get_matches(self.player_id)

        options = []
        if len(matches) > 24:
            matches = matches[0:24]

        for i, n in enumerate(matches):
            options.append({
                "label": "{}번째".format(i+1),
                "value": i,
                "description": n
            })
        options.append({
            "label": "업데이트",
            "value": "update",
            "description": "전적 정보를 업데이트 합니다.",
            "emoji": discord.PartialEmoji(id=868344053262061578, name="update").to_dict()
        })

        embed = discord.Embed(
            title="매치 선택",
            description="검색하실 매치를 선택해주세요. 목록을 업데이트 할 경우 업데이트를 선택해주세요.",
            color=0xffd619
        )
        last_update = self.database2.get_lastupdate(player_id=self.player_id, cls=pubgpy.Player)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")
        components = [
            ActionRow(components=[
                Selection(
                    custom_id="matches_selection",
                    options=options,
                    min_values=1,
                    max_values=1,
                )
            ])
        ]
        if b_msg is None:
            b_msg = await self.ctx.send(embed=embed, components=components)
        else:
            await b_msg.edit(embed=embed, components=components)
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg, Selection()))
        await resp.defer_update()

        if "update" in resp.values:
            return await self.choice_match(b_msg=b_msg)
        else:
            return b_msg, int(resp.values[0])

    async def match_stats(self, match_id: str, b_msg: Message = None):
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)
        player_data: pubgpy.Participant = data.get_player_id(player_id=self.player_id)
        team_data: pubgpy.Roster = data.get_team(player_id=self.player_id)

        team_member = [data.get_player_id(i).name for i in team_data.teams]
        map_nm = data.map
        playtime = datetime.fromtimestamp(float(player_data.time_survived), timezone('UTC'))

        kills = player_data.kills
        assists = player_data.assists
        death_tp = player_data.death_type
        distance = player_data.walk_distance + player_data.swim_distance + player_data.ride_distance
        deals = player_data.damage_dealt
        rank = player_data.win_place

        embed = discord.Embed(color=0xffd619)
        embed.add_field(name="팀원:", value=",".join(team_member), inline=False)
        embed.add_field(name="결과:", value=f'{death_reason(death_tp)}({rank}위)', inline=True)
        embed.add_field(name="맵:", value=map_id[map_nm], inline=True)
        embed.add_field(name="킬/어시:", value=f"{kills}회/{assists}회", inline=True)
        embed.add_field(name="생존시간:", value=f"{get_time_to_string(playtime)}", inline=True)
        embed.add_field(name="이동한 거리:", value=f"{distance} km", inline=True)
        embed.add_field(name="딜량:", value=f"{round(deals, 2)}", inline=True)

        if b_msg is None:
            b_msg = await self.ctx.send(embed=embed)
        else:
            await b_msg.edit(embed=embed)
        return
