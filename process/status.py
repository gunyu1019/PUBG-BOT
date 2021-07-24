import discord

from pytz import timezone
from datetime import datetime
from typing import Union
from module import pubgpy
from module.components import ActionRow, Button
from module.interaction import SlashContext, Message
from utils.cache import CacheData
from utils.directory import directory
from utils.time import get_time_to_string

image_name = {
    "steam": "steam.png",
    "kakao": "kakao.png",
    "xbox": "xbox.png",
    "psn": "playstation.png",
    "stadia": "stadia.png"
}


total_player_btn = Button(
    style=1,
    emoji=discord.PartialEmoji(id=868342431177900074, name="bar"),
    custom_id="total"
)
solo_player_btn = Button(
    style=1,
    emoji=discord.PartialEmoji(id=868178845373726790, name="solo"),
    custom_id="solo"
)
duo_player_btn = Button(
    style=1,
    emoji=discord.PartialEmoji(id=868342471556472853, name="duo"),
    custom_id="duo"
)
squad_player_btn = Button(
    style=1,
    emoji=discord.PartialEmoji(id=868342471187374120, name="squad"),
    custom_id="squad"
)
update_btn = Button(
    label="업데이트",
    style=1,
    emoji=discord.PartialEmoji(id=868344053262061578, name="update"),
    custom_id="update"
)


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
        self.database = CacheData(self.pubg)
        self.player_nickname = player
        self.player_id = player_id
        self.player = self.pubg.player_id(self.player_id)
        self.season = season

    @property
    def platform(self):
        return self.pubg.platform().value

    def _platform_file(self) -> discord.File:
        return discord.File(f"{directory}/assets/Icon/{image_name[self.platform]}")

    async def _normal_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.get_playdata(player_id=player_id, season=self.season, cls=pubgpy.SeasonStats)

    async def _ranked_data(self, player_id) -> pubgpy.GameModeReceive:
        return await self.database.get_playdata(player_id=player_id, season=self.season, cls=pubgpy.RankedStats)

    @staticmethod
    def _get_kill_death_points(kills: int, deaths: int, assists: int = 0) -> float:
        if int(deaths) != 0:
            kill_death_points = round((kills + assists) / int(deaths), 2)
        else:
            kill_death_points = round(float(kills + assists), 2)
        return kill_death_points

    async def normal_total(self, fpp: bool = False):
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

        await self.ctx.send(
            file=self._platform_file(), embed=embed,
            components=[
                ActionRow(components=[solo_player_btn, duo_player_btn, squad_player_btn, update_btn])
            ]
        )

    async def ranked_total(self, fpp: bool = False):
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

            embed.add_field(
                name=f"{n}:",
                value=f"랭크: {str(tier)}({tier.point}점)\n{wins}승 {top10s}탑 {losses}패\n킬: {kills}회({kill_death_points}점)",
                inline=True
            )
        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.RankedStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")

        await self.ctx.send(
            file=self._platform_file(), embed=embed,
            components=[
                ActionRow(components=[solo_player_btn, squad_player_btn, update_btn])
            ]
        )

    async def normal_mode(self, mode: str):
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

        await self.ctx.send(
            file=self._platform_file(), embed=embed,
            components=[
                ActionRow(components=[total_player_btn, update_btn])
            ]
        )

    async def ranked_mode(self, mode: str):
        section = await self._ranked_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=f"{self.player_nickname}님의 전적")

        data: pubgpy.RankedStats = getattr(section, mode)
        # TODO -> Fix pubgpy..? (data error)
        current_tier = data.current
        best_tier = data.best
        avg_rank = data.avg_rank
        wins = data.wins
        top10s = data.top10s
        losses = data.deaths
        dbnos = data.dbnos
        assists = data.assists
        kills = data.kills
        deals = data.damage_dealt / 1 if data.rounds_played == 0 else data.rounds_played

        kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses, assists=assists)

        embed.add_field(name="현재 티어:", value=f"{str(current_tier)}({current_tier.point}점)", inline=True)
        embed.add_field(name="최고 티어:", value=f"{str(best_tier)}({best_tier.point}점)", inline=True)
        embed.add_field(name="승/탑/패:", value=f"{wins}승 {top10s}탑 {losses}패", inline=True)
        embed.add_field(name="킬(KDA):", value=f"{kills}회({kill_death_points}점)", inline=True)
        embed.add_field(name="어시:", value=f"{assists}회", inline=True)
        embed.add_field(name="dBNOs:", value=f"{dbnos}회", inline=True)
        embed.add_field(name="평균 순위:", value=f"{avg_rank}등", inline=True)
        embed.add_field(name="딜량:", value=f"{deals}", inline=True)

        last_update = self.database.get_lastupdate(player_id=self.player_id, cls=pubgpy.RankedStats)
        embed.set_footer(text=f"최근 업데이트: {last_update.strftime('%Y년 %m월 %d일 %p %I:%M')}")

        await self.ctx.send(
            file=self._platform_file(), embed=embed,
            components=[
                ActionRow(components=[total_player_btn, update_btn])
            ]
        )
