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

from discord.ext import interaction
from sqlalchemy.orm import sessionmaker

from config.config import get_config
from module import pubgpy

parser = get_config()


class Matches:
    def __init__(self, bot, factory):
        self.client: interaction.Client = bot
        self.factory = factory

        self.color = int(parser.get("Color", "default"), 16)
        self.error_color = int(parser.get("Color", "error"), 16)
        self.warning_color = int(parser.get("Color", "warning"), 16)

        self.pubgpy = pubgpy.Client(token=parser.get("Default", "pubg_token"))


def setup(client: interaction.Client, factory: sessionmaker):
    return client.add_interaction_cog(Matches(client, factory))
