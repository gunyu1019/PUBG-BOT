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
import json
import asyncio

from datetime import datetime
from typing import Union, Type
from pytz import timezone
from aiohttp import ClientSession
from discord.ext import interaction
from discord.ext.interaction import ActionRow, Button, Selection, ApplicationContext, ComponentsContext, Message

from config.config import parser
from module import pubgpy
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
            ctx: ApplicationContext,
            client: interaction.Client,
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
        self.cancel_btn = None
        self.init_button()

        self.before_func = None

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

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
        self.cancel_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(name="\U0000274C"),
            custom_id="cancel"
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
            self.map_total_btn,
            self.cancel_btn
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
    def check(ctx: Message, tp: Type[Union[Button, Selection]]):
        def check_func(component: ComponentsContext):
            return component.component_type == tp.TYPE and ctx.id == component.message.id
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
        elif custom_id == "cancel":
            return
        return

    async def choice_match(self, b_msg: Message = None):
        matches = await self.database2.get_matches(self.player_id)

        options = []
        if len(matches) > 23:
            matches = matches[0:23]

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
        options.append({
            "label": "취소",
            "value": "cancel",
            "description": "선택을 취소합니다.",
            "emoji": discord.PartialEmoji(name="\U0000274C").to_dict()
        })

        embed = discord.Embed(
            title="매치 선택",
            description="검색하실 매치를 선택해주세요. 목록을 업데이트 할 경우 업데이트를 선택해주세요.",
            color=self.color
        )
        last_update = await self.database2.get_lastupdate(player_id=self.player_id, cls=pubgpy.Player)
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
        try:
            resp: ComponentsContext = await self.client.wait_for_global_component(
                check=self.check(b_msg, Selection), timeout=300
            )
        except asyncio.TimeoutError:
            await self.database1.close()
            await self.database2.close()
            return

        try:
            await resp.defer_update()
        except discord.NotFound:
            pass

        if "update" in resp.values:
            return await self.choice_match(b_msg=b_msg)
        elif "cancel" in resp.values:
            embed = discord.Embed(
                title="매치 선택",
                description="~~검색하실 매치를 선택해주세요. 목록을 업데이트 할 경우 업데이트를 선택해주세요.~~\n"
                            "사용자 요청에 의하여 취소되었습니다.",
                color=self.color
            )
            await b_msg.edit(embed=embed, components=[])
            return None, None
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
        distance = round((player_data.walk_distance + player_data.swim_distance + player_data.ride_distance)/1000, 2)
        deals = round(player_data.damage_dealt, 2)
        rank = player_data.win_place

        embed = discord.Embed(color=self.color)
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
                embed=embed, attachment=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )

        try:
            resp: ComponentsContext = await self.client.wait_for_global_component(check=self.check(b_msg, Button), timeout=300)
        except asyncio.TimeoutError:
            await self.database1.close()
            await self.database2.close()
            return

        try:
            await resp.defer_update()
        except discord.NotFound:
            pass
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return

    async def team_status(self, match_id: str, b_msg: Message = None):
        self.before_func = self.team_status
        data: pubgpy.Matches = await self.database1.get_match(matches_id=match_id)

        player_data: pubgpy.Participant = data.get_player_id(player_id=self.player_id)
        team_data: pubgpy.Roster = data.get_team(player_id=player_data.id)

        embed = discord.Embed(color=self.color)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 플레이 내역")
        team_member = [data.filter(filter_id=i, base_model=pubgpy.Participant) for i in team_data.teams]
        for member in team_member:
            kills = member.kills
            assists = member.assists
            playtime = datetime.fromtimestamp(float(member.time_survived), timezone('UTC'))
            distance = round((member.walk_distance + member.swim_distance + member.ride_distance)/1000, 2)
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
                embed=embed, attachment=self._platform_file(), components=[
                    ActionRow(components=self.button)
                ]
            )

        try:
            resp: ComponentsContext = await self.client.wait_for_global_component(check=self.check(b_msg, Button), timeout=300)
        except asyncio.TimeoutError:
            await self.database1.close()
            await self.database2.close()
            return

        try:
            await resp.defer_update()
        except discord.NotFound:
            pass
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

        embed = discord.Embed(color=self.color)
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
                embed=embed, attachments=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )

        try:
            resp: ComponentsContext = await self.client.wait_for_global_component(check=self.check(b_msg, Button), timeout=300)
        except asyncio.TimeoutError:
            await self.database1.close()
            await self.database2.close()
            return

        try:
            await resp.defer_update()
        except discord.NotFound:
            pass
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

        embed = discord.Embed(color=self.color)
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
                embed=embed, attachments=[self._platform_file(), file], components=[
                    ActionRow(components=self.button)
                ]
            )
        try:
            resp: ComponentsContext = await self.client.wait_for_global_component(check=self.check(b_msg, Button), timeout=300)
        except asyncio.TimeoutError:
            await self.database1.close()
            await self.database2.close()
            return

        try:
            await resp.defer_update()
        except discord.NotFound:
            pass
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, match_id=match_id)
        return
