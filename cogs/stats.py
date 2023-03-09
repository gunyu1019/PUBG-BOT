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

from config.config import get_config
from models import database
from module.statsType import StatsType
from module import pubgpy
from process.player import Player
from process.stats import Stats as StatsProcess

parser = get_config()
platform_choices = [
    interaction.CommandOptionChoice(name='스팀', value='steam'),
    interaction.CommandOptionChoice(name='카카오', value='kakao'),
    interaction.CommandOptionChoice(name='XBOX', value='xbox'),
    interaction.CommandOptionChoice(name='플레이스테이션', value='psn')
]


def stats_option_nickname():
    return interaction.option(name='닉네임', description='플레이어의 닉네임을 입력해주세요.', required=True)


def stats_option_season():
    return interaction.option(
        name='시즌',
        description='조회하는 전적 정보의 배틀그라운드 시즌 정보가 입력됩니다.',
        min_value=1,
        required=False
    )


def stats_option_platform():
    return interaction.option(
        name='플랫폼',
        description='플레이어의 플랫폼을 입력합니다. (이전에 이미 플랫폼을 선택한 경우에 작성할 필요는 없습니다.)',
        choices=platform_choices,
        required=False
    )


class Stats:
    def __init__(self, bot, factory):
        self.client: interaction.Client = bot
        self.factory = factory

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))

    @interaction.command(name='전적')
    async def stats(self, ctx: interaction.ApplicationContext):
        pass

    @stats.subcommand(name="1인칭_일반", description='배틀그라운드 사용자의 일반(1인칭) 전적 정보를 불러옵니다.')
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_1st(
            self,
            ctx: interaction.ApplicationContext,
            player: str,
            season: int = None,
            platform: str = None
    ):
        return await self._stats_base(ctx, StatsType.Ranked_1st, player, season, platform)

    @stats.subcommand(name="일반", description='배틀그라운드 사용자의 일반 전적 정보를 불러옵니다.')
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_3rd(
            self,
            ctx: interaction.ApplicationContext,
            player: str,
            season: int = None,
            platform: str = None
    ):
        return await self._stats_base(ctx, StatsType.Normal_3rd, player, season, platform)

    @stats.subcommand(name="랭크", description='배틀그라운드 사용자의 랭크 전적 정보를 불러옵니다.')
    @stats_option_nickname()
    @stats_option_season()
    @stats_option_platform()
    async def stats_normal_3rd(
            self,
            ctx: interaction.ApplicationContext,
            player: str,
            season: int = None,
            platform: str = None
    ):
        return await self._stats_base(ctx, StatsType.Ranked_3rd, player, season, platform)

    async def _stats_base(
            self,
            ctx: interaction.ApplicationContext,
            stats_type: StatsType,
            player: str,
            season: int = None,
            platform: str = None
    ):
        session: AsyncSession = self.factory.__call__()
        await ctx.defer()

        _player = Player(ctx, self.client, self.pubgpy, session, ctx.locale)

        # 배틀그라운드 플레이어 정보 불러오기
        player_info = await _player.player(player)
        if player_info is None:
            return

        # 최신 시즌 정보 불러오기
        if season is None:
            query = (
                select(database.CurrentSeasonInfo).where(database.CurrentSeasonInfo.platform == player_info.platform)
            )
            season_data: database.CurrentSeasonInfo = await session.scalar(query)
            season = season_data.season

        stats_session = StatsProcess(ctx, self.client, self.factory, player_info.player, season, fpp=False)
        await stats_session.update_data(database.NormalStats, session, update=False)

        # 사용자 정보만 불러오고 닫기
        await session.close()

        match stats_type:
            case StatsType.Normal_1st:
                pass
            case StatsType.Normal_3rd:
                pass
            case StatsType.Ranked_3rd:
                pass
            case StatsType.Ranked_1st:
                pass
        return


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(Stats(client, factory))
