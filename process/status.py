"""GNU GENERAL PUBLIC LICENSE

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

from pytz import timezone
from datetime import datetime
from typing import Union, Optional
from module import pubgpy
from module.components import ActionRow, Button
from module.interaction import SlashContext, Message, ComponentsContext
from utils.cache import CachePlayData
from utils.directory import directory
from utils.time import get_time_to_string

image_name = {
    "steam": "steam.png",
    "kakao": "kakao.png",
    "xbox": "xbox.png",
    "psn": "playstation.png",
    "stadia": "stadia.png"
}


class Status:
    def __init__(
            self,
            ctx: Union[SlashContext, Message],
            client: discord.Client,
            pubg: pubgpy.Client,
            player: str,
            player_id: str,
            season: pubgpy.Season
    ):
        self.ctx = ctx
        self.client = client
        self.pubg = pubg
        self.database = CachePlayData(self.pubg)
        self.player_nickname = player
        self.player_id = player_id
        self.player = self.pubg.player_id(self.player_id)
        self.season = season

        self.before_func = None
        self.before_mode: Optional[Union[bool, str]] = None

        self.total_player_btn = None
        self.solo_player_btn = None
        self.duo_player_btn = None
        self.squad_player_btn = None
        self.update_btn = None
        self.init_button()

    def init_button(self):
        self.total_player_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868342431177900074, name="bar"),
            custom_id="total"
        )
        self.solo_player_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868178845373726790, name="solo"),
            custom_id="solo"
        )
        self.duo_player_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868342471556472853, name="duo"),
            custom_id="duo"
        )
        self.squad_player_btn = Button(
            style=1,
            emoji=discord.PartialEmoji(id=868342471187374120, name="squad"),
            custom_id="squad"
        )
        self.update_btn = Button(
            label="업데이트",
            style=1,
            emoji=discord.PartialEmoji(id=868344053262061578, name="update"),
            custom_id="update"
        )

    @property
    def button(self):
        return [
            self.total_player_btn,
            self.solo_player_btn,
            self.duo_player_btn,
            self.squad_player_btn,
            self.update_btn
        ]

    @property
    def platform(self):
        return self.pubg.platform().value

    def _platform_file(self) -> discord.File:
        return discord.File(f"{directory}/assets/Icon/{image_name[self.platform]}")

    async def _normal_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.get_playdata(player_id=player_id, season=self.season, cls=pubgpy.SeasonStats)

    async def _ranked_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.get_playdata(player_id=player_id, season=self.season, cls=pubgpy.RankedStats)

    async def _normal_update_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.update_playdata(player_id=player_id, season=self.season, cls=pubgpy.SeasonStats)

    async def _ranked_update_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.update_playdata(player_id=player_id, season=self.season, cls=pubgpy.RankedStats)

    @staticmethod
    def _get_kill_death_points(kills: int, deaths: int, assists: int = 0) -> float:
        if int(deaths) != 0:
            kill_death_points = round((kills + assists) / int(deaths), 2)
        else:
            kill_death_points = round(float(kills + assists), 2)
        return kill_death_points

    @staticmethod
    def _rank(tier: pubgpy.Rank):
        if tier.tier is None:
            return "Unranked"
        elif tier.subtier is not None:
            return f"{tier.tier} {tier.subtier}"
        return f"{tier.tier}"

    @staticmethod
    def _get_rank_file(tier: pubgpy.Rank):
        if tier.tier is None:
            return "Unranked.png"
        elif tier.subtier is not None:
            return f"{tier.tier}-{tier.subtier}.png"
        return f"{tier.tier}.png"

    @staticmethod
    def _rank_point(tier: pubgpy.Rank):
        return tier.point if tier.point is not None else 0

    @staticmethod
    def check(ctx: Message):
        def check_func(component: ComponentsContext):
            return component.component_type == 2 and ctx.id == component.message.id
        return check_func

    def current_button(self):
        self.init_button()
        if self.before_func == self.ranked_total or self.before_func == self.normal_total:
            self.total_player_btn.style = 3
        elif isinstance(self.before_mode, str):
            getattr(self, "{}_player_btn".format(self.before_mode), Button()).style = 3
        return

    async def response(self, b_msg: Message, custom_id: str, fpp: bool = False, ranked: bool = False):
        if custom_id == "update":
            if ranked:
                await self._ranked_update_data(self.player_id)
            else:
                await self._normal_update_data(self.player_id)
            if isinstance(self.before_mode, bool):
                await self.before_func(fpp=self.before_mode, b_msg=b_msg)
            else:
                await self.before_func(mode=self.before_mode, b_msg=b_msg)

        if ranked:
            if custom_id == "total":
                await self.ranked_total(fpp=fpp, b_msg=b_msg)
            else:
                await self.ranked_mode(mode="{}_fpp".format(custom_id) if fpp else custom_id, b_msg=b_msg)
        else:
            if custom_id == "total":
                await self.normal_total(fpp=fpp, b_msg=b_msg)
            else:
                await self.normal_mode(mode="{}_fpp".format(custom_id) if fpp else custom_id, b_msg=b_msg)

    async def normal_total(self, fpp: bool = False, b_msg: Message = None):
        self.before_func = self.normal_total
        self.before_mode = fpp
        section = await self._normal_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 전적")

        if not fpp:
            game_mode = ["solo", "duo", "squad"]
            list_name = ["솔로(Solo)", "듀오(Duo)", "스쿼드(Squad)"]
        else:
            game_mode = ["solo_fpp", "duo_fpp", "squad_fpp"]
            list_name = ["솔로 1인칭(Solo)", "듀오 1인칭(Duo)", "스쿼드 1인칭(Squad)"]

        for i, n in enumerate(list_name):
            data: pubgpy.SeasonStats = getattr(section, game_mode[i])
            wins = data.wins
            top10s = data.top10s
            losses = data.losses
            assists = data.assists
            kills = data.kills

            playtime_floated = data.time_survived
            playtime_datetime = datetime.fromtimestamp(playtime_floated, timezone('UTC'))
            playtime = get_time_to_string(playtime_datetime)

            kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses, assists=assists)

            embed.add_field(
                name=f"{n}:",
                value=f"{wins}승 {top10s}탑 {losses}패\n{playtime}\n킬: {kills}회({kill_death_points}점)",
                inline=True
            )
        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.SeasonStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")
        self.current_button()

        if b_msg is None:
            b_msg = await self.ctx.send(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, fpp=fpp)
        return

    async def ranked_total(self, fpp: bool = False, b_msg: Message = None):
        self.before_func = self.ranked_total
        self.before_mode = fpp
        section = await self._ranked_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 전적")

        if not fpp:
            game_mode = ["solo", "squad"]
            list_name = ["솔로(Solo)", "스쿼드(Squad)"]
        else:
            game_mode = ["solo_fpp", "squad_fpp"]
            list_name = ["솔로 1인칭(Solo)", "스쿼드 1인칭(Squad)"]

        for i, n in enumerate(list_name):
            data: pubgpy.RankedStats = getattr(section, game_mode[i])
            tier = data.current

            wins = data.wins
            top10s = data.top10s
            losses = data.deaths
            kills = data.kills
            assists = data.assists
            kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses, assists=assists)

            point = self._rank_point(tier)
            rank = self._rank(tier)
            embed.add_field(
                name=f"{n}:",
                value=f"랭크: {rank}({point}점)\n{wins}승 {top10s}탑 {losses}패\n킬: {kills}회({kill_death_points}점)",
                inline=True
            )
        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.RankedStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")
        self.current_button()
        self.duo_player_btn.disabled = True

        if b_msg is None:
            b_msg = await self.ctx.send(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, fpp=fpp, ranked=True)
        return

    async def normal_mode(self, mode: str, b_msg: Message = None):
        self.before_func = self.normal_mode
        self.before_mode = mode
        section = await self._normal_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 전적")

        data: pubgpy.SeasonStats = getattr(section, mode)
        wins = data.wins
        top10s = data.top10s
        losses = data.losses
        dbnos = data.dbnos
        max_kill_streaks = data.max_kill_streaks
        assists = data.assists
        kills = data.kills
        headshot = data.headshot_kills
        deals = data.damage_dealt / 1 if data.rounds_played == 0 else data.rounds_played
        distance = data.ride_distance + data.swim_distance + data.walk_distance

        playtime_floated = data.time_survived
        playtime_datetime = datetime.fromtimestamp(playtime_floated, timezone('UTC'))
        playtime = get_time_to_string(playtime_datetime)

        kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses, assists=assists)

        embed.add_field(name="승/탑/패:", value=f"{wins}승 {top10s}탑 {losses}패", inline=True)
        embed.add_field(name="플레이타임:", value=f"{playtime}", inline=True)
        embed.add_field(name="킬(KDA):", value=f"{kills}회({kill_death_points}점)", inline=True)
        embed.add_field(name="어시:", value=f"{assists}회", inline=True)
        embed.add_field(name="dBNOs:", value=f"{dbnos}회", inline=True)
        embed.add_field(name="여포:", value=f"{max_kill_streaks}회", inline=True)
        embed.add_field(name="헤드샷:", value=f"{headshot}%", inline=True)
        embed.add_field(name="딜량:", value=f"{deals}", inline=True)
        embed.add_field(name="거리:", value=f"{distance}m", inline=True)

        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.RankedStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")
        self.current_button()

        if b_msg is None:
            b_msg = await self.ctx.send(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                file=self._platform_file(), embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, fpp=mode.endswith("_fpp"))
        return

    async def ranked_mode(self, mode: str, b_msg: Message = None):
        self.before_func = self.ranked_mode
        self.before_mode = mode
        section = await self._ranked_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 전적")

        data: pubgpy.RankedStats = getattr(section, mode)
        current_tier = data.current
        best_tier = data.best
        avg_rank = data.avg_rank

        current_point = self._rank_point(current_tier)
        current_rank = self._rank(current_tier)
        best_point = self._rank_point(best_tier)
        best_rank = self._rank(best_tier)

        wins = data.wins
        losses = data.deaths
        top10s = data.top10s
        kills = data.kills
        assists = data.assists
        dbnos = data.dbnos
        deals = data.damage_dealt / 1 if data.rounds_played == 0 else data.rounds_played

        kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses, assists=assists)
        filename = self._get_rank_file(current_tier)
        file = discord.File(fp=f"{directory}/assets/Insignias/{filename}", filename=filename)

        embed.add_field(name="현재 티어:", value=f"{current_rank}({current_point}점)", inline=True)
        embed.add_field(name="최고 티어:", value=f"{best_rank}({best_point}점)", inline=True)
        embed.add_field(name="승/탑/패:", value=f"{wins}승 {top10s}탑 {losses}패", inline=True)
        embed.add_field(name="킬(KDA):", value=f"{kills}회({kill_death_points}점)", inline=True)
        embed.add_field(name="어시:", value=f"{assists}회", inline=True)
        embed.add_field(name="dBNOs:", value=f"{dbnos}회", inline=True)
        embed.add_field(name="평균 순위:", value=f"{avg_rank}등", inline=True)
        embed.add_field(name="딜량:", value=f"{deals}", inline=True)
        embed.set_thumbnail(url=f"attachment://{filename}")

        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.RankedStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")
        self.current_button()
        self.duo_player_btn.disabled = True

        if b_msg is None:
            b_msg = await self.ctx.send(
                files=[self._platform_file(), file], embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        else:
            await b_msg.edit(
                files=[self._platform_file(), file], embed=embed,
                components=[
                    ActionRow(components=self.button)
                ]
            )
        resp: ComponentsContext = await self.client.wait_for("components", check=self.check(b_msg))
        await resp.defer_update()
        await self.response(b_msg=b_msg, custom_id=resp.custom_id, fpp=mode.endswith("_fpp"), ranked=True)
        return
