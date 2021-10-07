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
import pymysql
import json

from discord.ext.commands.context import Context
from typing import Union, List
from module.interaction import ApplicationContext
from module.message import Message
from utils.database import get_database
from config.config import parser


class PrefixClass:
    def __init__(self, bot: discord.Client):
        self.bot = bot

        self.default_prefixes = list(
            json.loads(
                parser.get("DEFAULT", "default_prefixes")
            )
        )

        self.prefix_caches = {}

    @property
    def default_prefix(self):
        if len(self.default_prefixes) == 1:
            return self.default_prefixes[0]
        return self.default_prefixes

    def bot_prefix(
            self,
            bot: discord.Client,
            context: Union[discord.Message, ApplicationContext, Message, Context]
    ):
        if context.guild is not None:
            if context.guild.id in self.prefix_caches:
                return self.prefix_caches[context.guild.id]
            return self.load_prefix(guild=context.guild, caching=True)
        return self.default_prefixes

    def load_prefixes(self) -> None:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)

        command = pymysql.escape_string(f"select id, prefix from SERVER_INFO")
        cur.execute(command)
        prefixes = cur.fetchall()
        for data in prefixes:
            guild_id = data.get("id")
            prefix = data.get("prefix")
            self.prefix_caches[int(guild_id)] = prefix
        cur.close()
        connect.close()

        for guild in self.bot.guilds:
            if not self.check_prefix(guild):
                self.prefix_caches[int(guild.id)] = self.default_prefix
        return

    def load_prefix(
            self,
            guild: discord.Guild,
            caching: bool = False
    ) -> List[str]:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)

        command = pymysql.escape_string(f"select prefix from SERVER_INFO WHERE id = %s")
        cur.execute(command, guild.id)
        data = cur.fetchone()
        if data is None or data == {}:
            prefix = self.default_prefix
        else:
            prefix = data.get("prefix")

        if caching:
            if not self.check_prefix(guild):
                self.prefix_caches[int(guild.id)] = prefix
        return prefix

    @staticmethod
    def check_prefix_in_database(guild: discord.Guild) -> bool:
        if guild is not None:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            sql_prefix = pymysql.escape_string(
                f"select EXISTS (select prefix from SERVER_INFO where ID=%s) as success"
            )
            cur.execute(sql_prefix, guild)
            result = cur.fetchone()['success']
            connect.close()
            return bool(result)
        return False

    def check_prefix(self, guild: discord.Guild) -> bool:
        if guild is not None:
            return int(guild.id) in self.prefix_caches
        return False

    def set_prefix(
            self,
            guild: discord.Guild,
            prefix
    ):
        if guild is not None:
            connect = get_database()
            cur = connect.cursor(pymysql.cursors.DictCursor)
            if self.check_prefix_in_database(guild):
                sql_prefix = pymysql.escape_string("update SERVER_INFO set prefix=%s where ID=%s")
            else:
                sql_prefix = pymysql.escape_string("insert into SERVER_INFO(prefix, ID) values (%s, %s)")
            cur.execute(sql_prefix, (prefix, guild.id))
            connect.commit()
            connect.close()

            self.prefix_caches[int(guild.id)] = prefix
        return
