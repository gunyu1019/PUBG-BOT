import discord
import json

from datetime import datetime
from typing import Union
from pytz import timezone
from aiohttp import ClientSession

from module import pubgpy
from module.components import ActionRow, Button, Selection
from module.interaction import SlashContext, Message, ComponentsContext
from utils.cache import CacheMatches, CacheMatchesList
from utils.directory import directory
from utils.map_image import MapData
from utils.time import get_time_to_string

with open(f"{directory}/data/deathReason.json", "r", encoding='utf-8') as f:
    death_reason = json.load(f)
with open(f"{directory}/data/mapName.json", "r", encoding='utf-8') as f:
    map_id = json.load(f)

image_name = {
    "steam": "steam.png",
    "kakao": "kakao.png",
    "xbox": "xbox.png",
    "psn": "playstation.png",
    "stadia": "stadia.png"
}


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
        self.image = None
        self.assets_data = None

        self.status_btn = None
        self.team_status_btn = None
        self.map_death_btn = None
        self.map_total_btn = None
        self.init_button()

        self.before_func = None

    def init_button(self):
        self.status_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868178845373726790, name="solo"),
            custom_id="status"
        )
        self.team_status_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868342471187374120, name="squad"),
            custom_id="team_status"
        )
        self.map_death_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=871401992122167337, name="map_death"),
            custom_id="map_death"
        )
        self.map_total_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=871401991937605652, name="map_icon"),
            custom_id="map_total"
        )

    @property
    def platform(self):
        return self.pubg.platform().value

    def _platform_file(self) -> discord.File:
        return discord.File(f"{directory}/assets/Icon/{image_name[self.platform]}")

    @property
    def button(self):
        return [
            self.status_btn,
            self.team_status_btn,
            self.map_death_btn,
            self.map_total_btn
        ]

    def current_button(self, data):
        self.init_button()
        if len(data.asset) == 0:
            self.map_total_btn.disabled = True
            self.map_death_btn.disabled = True

        if data.gamemode == pubgpy.GameMode.solo or data.gamemode == pubgpy.GameMode.solo_fpp:
            self.team_status_btn.disabled = True

        if self.before_func == self.match_stats:
            self.status_btn.style = 3
        if self.before_func == self.team_status:
            self.team_status_btn.style = 3
        if self.before_func == self.map_total:
            self.map_total_btn.style = 3
        if self.before_func == self.map_death:
            self.map_death_btn.style = 3
        return

    @staticmethod
    def check(ctx: Message, tp: Union[Button, Selection]):
        def check_func(component: ComponentsContext):
            return component.component_type == tp.type and ctx.id == component.message.id
        return check_func

    async def get_assets(self, data: pubgpy.Matches):
        if self.assets_data is None:
            if len(data.asset) == 0:
                return None
            link = data.asset[0].url
            async with ClientSession() as session:
                async with session.request(method="GET", url=link) as resp:
                    self.assets_data = await resp.json()
        return self.assets_data

    async def response(self, b_msg: Message, custom_id: str, match_id: str):
        if custom_id == "status":
            await self.match_stats(match_id=match_id, b_msg=b_msg)
        elif custom_id == "team_status":
            await self.team_status(match_id=match_id, b_msg=b_msg)
        elif custom_id == "map_death":
            await self.map_death(match_id=match_id, b_msg=b_msg)
        elif custom_id == "map_total":
            await self.map_total(match_id=match_id, b_msg=b_msg)
        return

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
        self.before_func = self.match_stats
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)

        player_data: pubgpy.Participant = data.get_player_id(player_id=self.player_id)
        team_data: pubgpy.Roster = data.get_team(player_id=player_data.id)

        team_member = [data.filter(filter_id=i, base_model=pubgpy.Participant).name for i in team_data.teams]
        map_nm = map_id.get(data.map.value)
        playtime = datetime.fromtimestamp(float(player_data.time_survived), timezone('UTC'))

        kills = player_data.kills
        assists = player_data.assists
        death_tp = death_reason.get(player_data.death_type.value)
        distance = player_data.walk_distance + player_data.swim_distance + player_data.ride_distance
        deals = round(player_data.damage_dealt, 2)
        rank = player_data.win_place

        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 플레이 내역")
        embed.add_field(name="팀원:", value=", ".join(team_member), inline=False)
        embed.add_field(name="결과:", value=f'{death_tp}({rank}위)', inline=True)
        embed.add_field(name="맵:", value=map_nm, inline=True)
        embed.add_field(name="킬/어시:", value=f"{kills}회/{assists}회", inline=True)
        embed.add_field(name="생존시간:", value=f"{get_time_to_string(playtime)}", inline=True)
        embed.add_field(name="이동한 거리:", value=f"{distance} km", inline=True)
        embed.add_field(name="딜량:", value=f"{deals}", inline=True)
        self.current_button(data)

        if b_msg is None:
            b_msg = await self.ctx.send(
                embed=embed, file=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                embed=embed, file=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg, Button()))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return

    async def team_status(self, match_id: str, b_msg: Message = None):
        self.before_func = self.team_status
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)

        player_data: pubgpy.Participant = data.get_player_id(player_id=self.player_id)
        team_data: pubgpy.Roster = data.get_team(player_id=player_data.id)

        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 플레이 내역")
        team_member = [data.filter(filter_id=i, base_model=pubgpy.Participant) for i in team_data.teams]
        for member in team_member:
            kills = member.kills
            assists = member.assists
            playtime = datetime.fromtimestamp(float(member.time_survived), timezone('UTC'))
            distance = member.walk_distance + member.swim_distance + member.ride_distance
            embed.add_field(
                name=member.name,
                value=f"킬/어시: {kills}회/{assists}회\n"
                      f"생존 시간: {get_time_to_string(playtime)}\n"
                      f"이동 거리: {distance}km",
                inline=True
            )
        self.current_button(data)

        if b_msg is None:
            b_msg = await self.ctx.send(
                embed=embed, file=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                embed=embed, file=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg, Button()))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return

    async def map_death(self, match_id: str, b_msg: Message = None):
        self.before_func = self.map_death
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)

        asset_data = await self.get_assets(data)
        self.image = MapData(player_id=self.player_id, map_name=data.map, data=asset_data)
        self.image.process()

        buf = self.image.save()
        file = discord.File(buf, filename="map_death.png")

        embed = discord.Embed(color=0xffd619)
        embed.description = "<:death:871414282435321868>: 죽음\n<:kill:871414283047678012>: 킬"
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 플레이 내역")
        embed.set_image(url="attachment://map_death.png")

        self.current_button(data)
        if b_msg is None:
            b_msg = await self.ctx.send(
                embed=embed, files=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                embed=embed, files=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg, Button()))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return

    async def map_total(self, match_id: str, b_msg: Message = None):
        self.before_func = self.map_total
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)

        asset_data = await self.get_assets(data)
        self.image = MapData(player_id=self.player_id, map_name=data.map, data=asset_data)
        self.image.process(revive=True, care_package=True)

        buf = self.image.save()
        file = discord.File(buf, filename="map_total.png")

        embed = discord.Embed(color=0xffd619)
        embed.description = "<:death:871414282435321868>: 죽음\n<:kill:871414283047678012>: " \
                            "킬\n<:revive:871414282770849852>: 회복\n<:care_package:871414282527584317>: 보급 상자\n "
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 플레이 내역")
        embed.set_image(url="attachment://map_total.png")

        self.current_button(data)
        if b_msg is None:
            b_msg = await self.ctx.send(
                embed=embed, files=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                embed=embed, files=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg, Button()))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return
