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
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import discord
import asyncio
import logging

from discord.ext import tasks

log = logging.getLogger(__name__)


class PresenceTask:
    def __init__(self, bot):
        self.client = bot
        self.presence.start()

    @tasks.loop(seconds=3)
    async def presence(self):
        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game("/도움말을 이용하여, 명령어를 알아보세요!"))
        await asyncio.sleep(3.0)

        shard = self.client.shard_count
        if shard is None:
            await self.client.change_presence(
                status=discord.Status.online,
                activity=discord.Game("활동중인 서버갯수: " + str(len(self.client.guilds)) + "개")
            )
        else:
            await self.client.change_presence(
                status=discord.Status.online,
                activity=discord.Game("활동중인 서버갯수: " + str(len(self.client.guilds)) + "개, 샤드갯수: " + str(shard) + "개")
            )
        await asyncio.sleep(3.0)

        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game("버그/피드백 등은 Developer Space 커뮤니티로 문의해주세요.")
        )
        await asyncio.sleep(3.0)

        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game("더 이상 접두어를 활용하여 사용할 수 없습니다 :(")
        )
        await asyncio.sleep(3.0)

        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game("배틀그라운드 공식 커뮤니티! https://discord.gg/pubgkorea")
        )
        await asyncio.sleep(3.0)

    @presence.before_loop
    async def before_booting(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_icog(PresenceTask(client))
