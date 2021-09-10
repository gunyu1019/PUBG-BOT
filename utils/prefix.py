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

import pymysql
import json

from utils.database import get_database
from config.config import parser

default_prefixes = list(json.loads(parser.get("DEFAULT", "default_prefixes")))


def get_prefix(bot, message):
    guild = message.guild
    if guild:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_prefix = pymysql.escape_string(f"select prefix from SERVER_INFO where ID={guild.id}")
        try:
            cur.execute(sql_prefix)
            prefix = cur.fetchone()
            if prefix is not None:
                a_prefix = prefix['prefix']
            else:
                a_prefix = default_prefixes[0]
        except pymysql.err.InternalError:
            a_prefix = default_prefixes[0]
        connect.close()
        return [a_prefix]
    else:
        return default_prefixes


def check_prefix(bot, guild):
    if guild is not None:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_prefix = pymysql.escape_string(f"select EXISTS (select prefix from SERVER_INFO where ID={guild.id}) as success")
        cur.execute(sql_prefix)
        True_or_False = cur.fetchone()['success']
        connect.close()
        return bool(True_or_False)


def set_prefix(bot, guild, prefix):
    if guild is not None:
        connect = get_database()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if check_prefix(bot, guild):
            sql_prefix = pymysql.escape_string("update SERVER_INFO set prefix=%s where ID=%s")
        else:
            sql_prefix = pymysql.escape_string("insert into SERVER_INFO(prefix, ID) values (%s, %s)")
        cur.execute(sql_prefix, (prefix, guild.id))
        connect.commit()
        connect.close()
