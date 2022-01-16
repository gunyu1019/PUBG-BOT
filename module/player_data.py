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

import aiohttp
import asyncio

from bs4 import BeautifulSoup
from typing import Tuple


class PlayerData:
    def __init__(self, loop: asyncio.BaseEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.BASE = "https://steamcommunity.com/app/578080"

    async def get_data(self) -> Tuple[bool, int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE) as resp:
                if resp.status == 200:
                    html = await resp.text()
                else:
                    return False, resp.status
        soup = BeautifulSoup(html, 'lxml')

        players = soup.find('span', {'class': 'apphub_NumInApp'}).text
        players = players.rstrip("In-Game").strip(" ").replace(",", "")
        return True, int(players)
