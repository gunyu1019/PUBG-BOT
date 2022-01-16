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

from config.config import parser
from utils.database import get_database

connect = get_database()

cur = connect.cursor(pymysql.cursors.DictCursor)
try:
    cur.execute("SELECT * from PUBG_BOT")
except pymysql.err.DatabaseError:
    client_list = {
        "token": parser.get("DEFAULT", "token"),
        "PUBG_API": parser.get("DEFAULT", "PUBG_API")
    }
else:
    if parser.getboolean('DEFAULT', 'database'):
        client_list = cur.fetchone()
    else:
        client_list = {
            "token": parser.get("DEFAULT", "token"),
            "PUBG_API": parser.get("DEFAULT", "PUBG_API")
        }

token = client_list.get('token')
PUBG_API = client_list.get('PUBG_API')

# Discord Bot Lists API TOKEN
DBL_token = client_list.get('topgg_token')
koreanBots_token = client_list.get('KoreanBots_token')
uniqueBots_token = client_list.get('UniqueBots_token')

connect.close()
