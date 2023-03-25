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

from typing import Type

import discord
from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from config.config import get_config
from models import database
from module import pubgpy
from process.stats import Stats as StatsProcess
from process.matches import MatchesProcess
from utils.location import comment

parser = get_config()


class Favorite:
    def __init__(self, bot, factory):
        self.client: interaction.Client = bot
        self.factory = factory

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))

    @interaction.command(name="즐겨찾기")
    async def fav_command(self):
        pass

    @fav_command.subcommand(name="일반", description="즐겨찾기한 사용자 중에서 일반 전적 정보를 불러옵니다.")
    async def favorite_normal_stats(self, ctx: interaction.ApplicationContext):
        await self.favorite_base(ctx, database.NormalStats, False)
        return

    @fav_command.subcommand(name="랭크", description="즐겨찾기한 사용자 중에서 랭크 전적 정보를 불러옵니다.")
    async def favorite_ranked_stats(self, ctx: interaction.ApplicationContext):
        await self.favorite_base(ctx, database.RankedStats, False)
        return

    @fav_command.subcommand(name="1인칭_일반", description="즐겨찾기한 사용자 중에서 일반 전적 정보를 불러옵니다.")
    async def favorite_normal_1st_stats(self, ctx: interaction.ApplicationContext):
        await self.favorite_base(ctx, database.NormalStats, True)
        return

    @fav_command.subcommand(name="1인칭_랭크", description="즐겨찾기한 사용자 중에서 랭크 전적 정보를 불러옵니다.")
    async def favorite_ranked_1st_stats(self, ctx: interaction.ApplicationContext):
        await self.favorite_base(ctx, database.RankedStats, True)
        return

    async def favorite_base(
        self,
        ctx: interaction.ApplicationContext,
        data_type: Type[database.RankedStats | database.NormalStats],
        fpp: bool,
    ):
        await ctx.defer()
        session: AsyncSession = self.factory.__call__()
        query = select(database.FavoritePlayer).where(
            database.FavoritePlayer.discord_id == ctx.author.id
        )
        data = await session.scalars(query)
        result: list[database.FavoritePlayer] = data.all()

        query = select(database.Player).where(
            database.Player.account_id.in_([x.player_id for x in result])
        )
        data = await session.scalars(query)
        result_player: list[database.Player] = data.all()

        player_data = {}
        for player in result_player:
            player_data[player.account_id] = {
                "name": player.name,
                "platform": player.platform,
            }

        embed = discord.Embed(
            description=comment("favorite", "description", ctx.locale), color=self.color
        )
        embed.set_author(
            icon_url=self.client.user.avatar.url,
            name=comment("favorite", "title", ctx.locale),
        )
        components = interaction.ActionRow(
            components=[
                interaction.Selection(
                    custom_id="favorite_player",
                    options=[
                        interaction.Options(
                            label=player_data.get(player.player_id, {}).get(
                                "name", "Unknown"
                            ),
                            description=player.player_id,
                            value=player.player_id,
                        )
                        for player in result
                    ],
                    min_values=1,
                    max_values=1,
                )
            ]
        )
        response = await ctx.send(embed=embed, components=[components])
        components_result: interaction.ComponentsContext = (
            await self.client.wait_for_component(
                custom_id="favorite_player",
                check=lambda x: x.author.id == ctx.author.id
                and x.message.id == response.id,
            )
        )
        await components_result.defer_update()
        player_id = components_result.values[0]
        player = self.pubgpy.player_id(player_id)
        player.name = player_data[player_id]["name"]
        player.client.platform(player_data[player_id]["platform"])
        query = select(database.CurrentSeasonInfo).where(
            database.CurrentSeasonInfo.platform == player_data[player_id]["platform"]
        )
        season_data: database.CurrentSeasonInfo = await session.scalar(query)
        season = season_data.season

        stats_process = StatsProcess(
            ctx=ctx,
            client=self.client,
            factory=self.factory,
            player=player,
            season=season,
            fpp=fpp,
        )
        stats_process.matches_class = MatchesProcess(
            ctx=stats_process.context,
            client=stats_process.client,
            factory=stats_process.factory,
            player=stats_process.player,
            stats=stats_process,
        )
        await stats_process.load_data(data_type, session)
        await stats_process.load_favorite(session)
        await session.close()

        match data_type:
            case database.RankedStats:
                await stats_process.ranked_stats()
            case database.NormalStats:
                await stats_process.normal_stats()
        return


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(Favorite(client, factory))
