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
from module import pubgpy
from models import database
from process.matches import MatchesProcess
from process.player import Player
from process.stats import Stats as StatsProcess
from utils.location import comment

parser = get_config()


class Matches:
    def __init__(self, bot, factory):
        self.client: interaction.Client = bot
        self.factory = factory

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))

    @interaction.command(name="매치", description="검색된 사용자의 플레이 내역를 불러옵니다.")
    @interaction.option(name="닉네임", description="플레이어의 닉네임을 입력해주세요.", required=True)
    @interaction.option(
        name="매치_순서", description="조회할 매치 순서를 입력해주세요.", required=False, min_value=1
    )
    async def match(
        self,
        ctx: interaction.ApplicationContext,
        player: str,
        matches_index: int = None,
    ):
        session: AsyncSession = self.factory.__call__()
        await ctx.defer()

        _player = Player(ctx, self.client, self.pubgpy, session, ctx.locale)

        # 배틀그라운드 플레이어 정보 불러오기
        player_info = await _player.player(player)
        if player_info is None:
            return

        query = select(database.CurrentSeasonInfo).where(
            database.CurrentSeasonInfo.platform == player_info.platform
        )
        season_data: database.CurrentSeasonInfo = await session.scalar(query)
        season = season_data.season
        matches_process = MatchesProcess(
            ctx=ctx, client=self.client, factory=self.factory, player=player_info.player
        )
        matches_process.stats_class = StatsProcess(
            ctx=matches_process.context,
            client=matches_process.client,
            factory=matches_process.factory,
            player=matches_process.player,
            matches=matches_process,
            season=season,
        )
        await matches_process.load_favorite(session)

        # await matches_process.load_matches_id(session)
        if matches_index is not None:
            _matches_ids = await matches_process.load_matches_id(session)
            if _matches_ids is None:
                return
            if len(_matches_ids) < matches_index + 1:
                embed = discord.Embed(
                    title=comment("matches_process", "title", ctx.locale),
                    description=comment(
                        "matches_process", "matches_index_out_of_range", ctx.locale
                    ),
                    color=self.warning_color,
                )
                await ctx.edit(embed=embed)
                return
            matches_id = _matches_ids[matches_index + 1]
        else:
            matches_id = await matches_process.match_selection(session)
        await session.close()
        if matches_id is None:
            return

        await matches_process.match_info(matches_id=matches_id)
        return


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(Matches(client, factory))
