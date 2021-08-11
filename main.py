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

import os

import discord
import pymysql.cursors
from discord.ext import commands

from config.config import parser
from config.log_config import log

from utils.database import get_database
from utils.prefix import get_prefix
from utils.token import token

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

    log.info("PUBG BOT을 불러오는 중입니다.")
    if parser.getboolean("DEFAULT", "AutoShard"):
        log.info("Config 파일에서 AutoShard가 켜져있습니다. AutoShard 기능을 킵니다.")
        bot = commands.AutoShardedBot(command_prefix=get_prefix, intents=discord.Intents.default())
    else:
        bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.default())

    database = get_database()
    cur = database.cursor(pymysql.cursors.DictCursor)

    bot.remove_command("help")
    cogs = ["cogs." + file[:-3] for file in os.listdir(f"{directory}/cogs") if file.endswith(".py")]
    for cog in cogs:
        bot.load_extension(cog)

    bot.run(token)
