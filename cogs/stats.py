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
from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncResult

from config.config import get_config
from models import database
from module.statsType import StatsType
from module import pubgpy
from process.player import Player
from process.stats import Stats as StatsProcess
from process.matches import MatchesProcess
from utils.location import comment


parser = get_config()
platform_choices = [
    interaction.CommandOptionChoice(name="스팀", value="steam"),
    interaction.CommandOptionChoice(name="카카오", value="kakao"),
    interaction.CommandOptionChoice(name="XBOX", value="xbox"),
    interaction.CommandOptionChoice(name="플레이스테이션", value="psn"),
]


def stats_option_nickname():
    return interaction.option(
        name="닉네임", description="플레이어의 닉네임을 입력해주세요.", required=True
    )


def stats_option_season():
    return interaction.option(
        name="시즌",
        description="조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.",
        min_value=1,
        required=False,
    )


def stats_option_platform():
    return interaction.option(
        name="플랫폼",
        description="플레이어의 플랫폼을 입력합니다. (이전에 이미 플랫폼을 선택한 경우에 작성할 필요는 없습니다.)",
        choices=platform_choices,
        required=False,
    )


class Stats:
    def __init__(self, bot, factory):
        self.client: interaction.Client = bot
        self.factory = factory

        self.color = int(parser.get("Color", "default"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)

        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))

    @interaction.command(name="전적")
    async def stats(self, ctx: interaction.ApplicationContext):
        pass

    @stats.subcommand(name="1인칭_일반", description="배틀그라운드 사용자의 일반(1인칭) 전적 정보를 불러옵니다.")
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_1st(
        self,
        ctx: interaction.ApplicationContext,
        player: str,
        season: int = None,
        platform: str = None,
    ):
        return await self._stats_base(
            ctx, StatsType.Ranked_1st, player, season, platform
        )

    @stats.subcommand(name="일반", description="배틀그라운드 사용자의 일반 전적 정보를 불러옵니다.")
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_3rd(
        self,
        ctx: interaction.ApplicationContext,
        player: str,
        season: int = None,
        platform: str = None,
    ):
        return await self._stats_base(
            ctx, StatsType.Normal_3rd, player, season, platform
        )

    @stats.subcommand(name="랭크", description="배틀그라운드 사용자의 랭크 전적 정보를 불러옵니다.")
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_3rd(
        self,
        ctx: interaction.ApplicationContext,
        player: str,
        season: int = None,
        platform: str = None,
    ):
        return await self._stats_base(
            ctx, StatsType.Ranked_3rd, player, season, platform
        )

    @interaction.command(name="플랫폼변경", description="사용자에 등록된 플랫폼 정보를 수정합니다.")
    @stats_option_nickname()
    async def stats_platform_selection(
        self, ctx: interaction.ApplicationContext, player: str
    ):
        session: AsyncSession = self.factory.__call__()
        await ctx.defer()

        _player = Player(ctx, self.client, self.pubgpy, session, ctx.locale)
        result = await _player.exist_player(nickname=player)
        if not result:
            await session.close()
            return
        origin_player_data = await _player.search_player(nickname=player)
        platform_info = await _player.player_platform()
        if platform_info is None:
            await session.close()
            return
        _platform = await _player.get_platform(platform_info)
        if _platform is None:
            await session.close()
            return

        player_data = database.Player(
            **{
                "name": origin_player_data.player.name,
                "account_id": origin_player_data.player.id,
                "platform": _platform,
            }
        )

        embed = discord.Embed(
            title=comment("platform", "platform_selection_title", ctx.locale),
            description=comment("platform", "platform_change_success", ctx.locale),
            color=self.color,
        )
        await ctx.edit(embed=embed)
        await session.merge(player_data)
        await session.commit()
        await session.close()
        return

    async def _stats_base(
        self,
        ctx: interaction.ApplicationContext,
        stats_type: StatsType,
        player: str,
        season: int = None,
        platform: str = None,
    ):
        session: AsyncSession = self.factory.__call__()
        await ctx.defer()

        _player = Player(ctx, self.client, self.pubgpy, session, ctx.locale)

        # 배틀그라운드 플레이어 정보 불러오기
        player_info = await _player.player(player, platform)
        if player_info is None:
            await session.close()
            return

        # 최신 시즌 정보 불러오기
        if season is None:
            query = select(database.CurrentSeasonInfo).where(
                database.CurrentSeasonInfo.platform == player_info.platform
            )
            season_data: database.CurrentSeasonInfo = await session.scalar(query)
            season = season_data.season
        else:
            if player_info.platform in [pubgpy.Platforms.STEAM, pubgpy.Platforms.KAKAO]:
                season = "division.bro.official.pc-2018-{}".format(season)
            elif player_info.platform in [
                pubgpy.Platforms.XBOX,
                pubgpy.Platforms.PLAYSTATION,
            ]:
                season = "division.bro.official.console-{}".format(season)

        stats_session = StatsProcess(
            ctx, self.client, self.factory, player_info.player, season, fpp=False
        )
        await stats_session.load_data(database.RankedStats, session)

        stats_process = StatsProcess(
            ctx=ctx,
            client=self.client,
            factory=self.factory,
            player=player_info.player,
            season=season,
            fpp=stats_type in [StatsType.Normal_1st, StatsType.Ranked_1st],
        )
        stats_process.matches_class = MatchesProcess(
            ctx=stats_process.context,
            client=stats_process.client,
            factory=stats_process.factory,
            player=stats_process.player,
            stats=stats_process,
        )
        await stats_process.load_data(
            database.RankedStats
            if stats_type in [StatsType.Ranked_1st, StatsType.Ranked_3rd]
            else database.NormalStats,  # [StatsType.Normal_1st, StatsType.Normal_3rd]
            session,
        )
        await stats_process.load_favorite(session)
        await session.close()

        if stats_type == StatsType.Normal_1st or stats_type == StatsType.Normal_3rd:
            await stats_process.normal_stats()
        elif stats_type == StatsType.Ranked_1st or stats_type == StatsType.Ranked_3rd:
            await stats_process.ranked_stats()
        return


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(Stats(client, factory))
