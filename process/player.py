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
import asyncio
import datetime
from typing import Optional, NamedTuple

import discord
from discord.ext import interaction
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, exists

from config.config import get_config
from models import database
from module import pubgpy
from process.request_loop import request_loop
from utils.location import comment

parser = get_config()

color = int(parser.get("Color", "default"), 16)
error_color = int(parser.get("Color", "error"), 16)
warning_color = int(parser.get("Color", "warning"), 16)

xbox = discord.PartialEmoji(name="XBOX", id=718482204035907586)
playstation = discord.PartialEmoji(name="PS", id=718482204417720400)
steam = discord.PartialEmoji(name="Steam", id=698454004656504852)
kakao = discord.PartialEmoji(name="kakao", id=718482204103278622)
stadia = discord.PartialEmoji(name="Stadia", id=718482205575348264)


class PlatformSelection(NamedTuple):
    player: pubgpy.Player
    platform: pubgpy.Platforms
    is_new_data: bool


class Player:
    def __init__(
        self,
        ctx: interaction.ApplicationContext,
        client: interaction.Client,
        pubg_client: pubgpy.Client,
        session: AsyncSession,
        language: str = "ko",
    ):
        self.ctx = ctx
        self.client = client
        self.pubg_client = pubg_client
        self.database = session
        self.language = language

    async def player(self, nickname: str) -> PlatformSelection:
        query = select(exists(database.Player).where(database.Player.name == nickname))
        data: AsyncResult = await self.database.execute(query)
        result = data.scalar_one_or_none()
        if result:
            query = select(database.Player).where(database.Player.name == nickname)
            player_info: database.Player = await self.database.scalar(query)
            player_data = self.pubg_client.player_id(player_info.account_id)
            player_data.name = player_info.name
            player_data.client.platform(player_info.platform)
            return PlatformSelection(player_data, player_info.platform, False)
        else:
            platform_selection = await self.player_platform(nickname=nickname)
            query = select(exists(database.Player).where(database.Player.account_id == platform_selection.player.id))
            data: AsyncResult = await self.database.execute(query)
            duplicated_account_id = data.scalar_one_or_none()
            player_data = database.Player(
                **{
                    "name": platform_selection.player.name,
                    "account_id": platform_selection.player.id,
                    "platform": platform_selection.platform.value,
                }
            )
            if not duplicated_account_id:
                # Player Data
                self.database.add(player_data)

                # Matches Data
                if len(platform_selection.player.matches) > 0:
                    queries = [
                        database.MatchesPlayer(
                            **{
                                "account_id_with_match_id": "{}_{}".format(
                                    platform_selection.player.id, match_id
                                ),
                                "account_id": platform_selection.player.id,
                                "match_id": match_id,
                                "match_index": index,
                                "last_update": datetime.datetime.now(),
                            }
                        )
                        for index, match_id in enumerate(platform_selection.player.matches)
                    ]
                    self.database.add_all(queries)
            else:
                await self.database.merge(player_data)
            await self.database.commit()
            return platform_selection

    async def player_platform(self, nickname: str) -> Optional[PlatformSelection]:
        embed = discord.Embed(
            title=comment("platform", "platform_selection_title", self.language),
            description=comment(
                "platform", "platform_selection_description", self.language
            ),
            color=color,
        )
        components = [
            interaction.ActionRow(
                components=[
                    interaction.Button(custom_id="steam", style=2, emoji=steam),
                    interaction.Button(custom_id="kakao", style=2, emoji=kakao),
                    interaction.Button(custom_id="xbox", style=2, emoji=xbox),
                    interaction.Button(custom_id="psn", style=2, emoji=playstation),
                ]
            )
        ]
        await self.ctx.edit(embed=embed, components=components)

        try:
            result: interaction.ComponentsContext = (
                await self.client.wait_for_global_component(
                    check=lambda x: (
                        x.custom_id in ["steam", "kakao", "xbox", "psn"]
                        and x.component_type == 2
                        and x.author.id == self.ctx.author.id
                    ),
                    timeout=300,
                )
            )
        except asyncio.TimeoutError:
            original_description = embed.description
            embed.description = original_description + comment(
                "result", "timeout_description", self.language
            )
            for index, _ in enumerate(components[0].components):
                components[0].components[index].disabled = True
            await self.ctx.edit(embed=embed, components=components)
            return

        embed.description = comment(
            "platform", "player_search_description", self.language
        )
        for index, _ in enumerate(components[0].components):
            components[0].components[index].disabled = True
        await result.update(embed=embed, components=components)

        platform_data = pubgpy.get_enum(pubgpy.Platforms, result.custom_id)
        if platform_data is None or platform_data == result.custom_id:
            embed = discord.Embed(
                title=comment("basic", "error", self.language),
                description=comment("platform", "platform_wrong", self.language),
                color=error_color,
            )
            await self.ctx.edit(embed=embed)
            return
        self.pubg_client.platform(platform_data)
        try:
            player_info = await request_loop(
                self.ctx, self.pubg_client.player, nickname=nickname
            )
        except pubgpy.NotFound:
            embed = discord.Embed(
                title=comment("basic", "error", self.language),
                description=comment(
                    "result", "player_not_found_description", self.language
                ),
                color=error_color,
            )
            await self.ctx.edit(embed=embed)
            return
        return PlatformSelection(player_info, platform_data, True)
