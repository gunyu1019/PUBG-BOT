import pymysql
import json

from utils.database import getDatabase
from config.config import parser

default_prefixes = list(json.loads(parser.get("DEFAULT", "default_prefixes")))


def get_prefix(bot, message):
    guild = message.guild
    if guild:
        connect = getDatabase()
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
        connect = getDatabase()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        sql_prefix = pymysql.escape_string(f"select EXISTS (select prefix from SERVER_INFO where ID={guild.id}) as success")
        cur.execute(sql_prefix)
        True_or_False = cur.fetchone()['success']
        connect.close()
        return bool(True_or_False)


def set_prefix(bot, guild, prefix):
    if guild is not None:
        connect = getDatabase()
        cur = connect.cursor(pymysql.cursors.DictCursor)
        if check_prefix(bot, guild):
            sql_prefix = pymysql.escape_string("update SERVER_INFO set prefix=%s where ID=%s")
        else:
            sql_prefix = pymysql.escape_string("insert into SERVER_INFO(prefix, ID) values (%s, %s)")
        cur.execute(sql_prefix, (prefix, guild.id))
        connect.commit()
        connect.close()
