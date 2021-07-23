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

# <:solo:868178845373726790> <:duo:868178863941886013> <:squad:868178845721829428>
solo_player_btn = Button(
    label="솔로",
    style=1,
    emoji=discord.PartialEmoji(id=868178845373726790, name="solo"),
    custom_id="solo"
)
duo_player_btn = Button(
    label="듀오",
    style=1,
    emoji=discord.PartialEmoji(id=868178863941886013, name="duo"),
    custom_id="duo"
)
squad_player_btn = Button(
    label="스쿼드",
    style=1,
    emoji=discord.PartialEmoji(id=868178845721829428, name="squad"),
    custom_id="squad"
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
        if int(deaths) is not 0:
            kill_death_points = round((kills + assists) / int(deaths), 2)
        else:
            kill_death_points = round(float(kills + assists), 2)
        return kill_death_points

    async def normal_total(self, fpp: bool = False):
        section = await self._normal_data(self.player_id)
        embed = discord.Embed(color=0xffd619)
        embed.set_author(icon_url="attachment://" + image_name[self.platform], name=self.player_nickname + "님의 전적")

        if not fpp:
            game_mode = ["solo", "duo", "squad"]
            list_name = ["솔로(Solo)", "듀오(Duo)", "스쿼드(Squad)"]
        else:
            game_mode = ["solo_fpp", "duo_fpp", "squad_fpp"]
            list_name = ["솔로 1인칭(Solo)", "듀오 1인칭(Duo)", "스쿼드 1인칭(Squad)"]

        for i, n in enumerate(list_name):
            data: pubgpy.SeasonStats = getattr(section, game_mode[i])
            win = data.wins
            top10s = data.top10s
            losses = data.losses
            kills = data.kills

            playtime_floated = data.time_survived
            playtime_datetime = datetime.fromtimestamp(playtime_floated, timezone('UTC'))
            playtime = get_time_to_string(playtime_datetime)

            kill_death_points = self._get_kill_death_points(kills=kills, deaths=losses)

            embed.add_field(
                name=f"{n}:",
                value=f"{win}승 {top10s}탑 {losses}패\n{playtime}\n킬: {kills}회({kill_death_points}점)",
                inline=True
            )

        await self.ctx.send(
            file=self._platform_file(), embed=embed,
            components=[
                ActionRow(components=[solo_player_btn, duo_player_btn, squad_player_btn])
            ]
        )
