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
from typing import Optional, NamedTuple, Any, Coroutine

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

    async def get_platform(self, platform_info: str) -> pubgpy.Platforms | None:
        _platform = pubgpy.get_enum(pubgpy.Platforms, platform_info)
        if _platform is None:
            embed = discord.Embed(
                title=comment("basic", "error", self.language),
                description=comment("platform", "platform_wrong", self.language),
                color=error_color,
            )
            await self.ctx.edit(embed=embed)
            return
        return _platform

    async def search_player(self, nickname: str) -> PlatformSelection:
        query = select(database.Player).where(database.Player.name == nickname)
        player_info: database.Player = await self.database.scalar(query)
        player_data = self.pubg_client.player_id(player_info.account_id)
        player_data.name = player_info.name
        player_data.client.platform(player_info.platform)
        return PlatformSelection(player_data, player_info.platform, False)

    async def exist_player(self, nickname: str) -> Coroutine[Any, Any, bool | None]:
        query = select(exists(database.Player).where(database.Player.name == nickname))
        data: AsyncResult = await self.database.execute(query)
        return data.scalar_one_or_none()

    async def player(
        self, nickname: str, platform_info: str | None = None
    ) -> Optional[PlatformSelection]:
        result = await self.exist_player(nickname)
        if result:
            player_data = await self.search_player(nickname)
            return player_data
        else:
            if platform_info is None:
                platform_info = await self.player_platform()
                if platform_info is None:
                    return
            _platform = await self.get_platform(platform_info)
            if _platform is None:
                return
            platform_selection = await self.insert_player(
                nickname=nickname, platform=_platform
            )
            if platform_selection is None:
                return

            query = select(
                exists(database.Player).where(
                    database.Player.account_id == platform_selection.player.id
                )
            )
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
                        for index, match_id in enumerate(
                            platform_selection.player.matches
                        )
                    ]
                    self.database.add_all(queries)
            else:
                await self.database.merge(player_data)
            await self.database.commit()
            return platform_selection

    async def player_platform(self) -> Optional[str]:
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
        message = await self.ctx.edit(embed=embed, components=components)

        try:
            result: interaction.ComponentsContext = (
                await self.client.wait_for_global_component(
                    check=lambda x: (
                        x.custom_id in ["steam", "kakao", "xbox", "psn"]
                        and x.component_type == 2
                        and x.author.id == self.ctx.author.id
                        and message.id == x.message.id
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

        for index, _ in enumerate(components[0].components):
            components[0].components[index].disabled = True

        embed = discord.Embed(
            title=comment("platform", "platform_selection_title", self.language),
            description=comment("platform", "player_search_description", self.language),
            color=color,
        )
        await result.update(embed=embed, components=components)

        return result.custom_id

    async def insert_player(self, nickname: str, platform: pubgpy.Platforms):
        self.pubg_client.platform(platform)
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
        return PlatformSelection(player_info, platform, True)
