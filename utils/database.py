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
import logging
from config.config import parser

log = logging.getLogger(__name__)


def get_database(database=None):
    for tries in ['MySQL1', 'MySQL2']:
        host = parser.get(tries, 'host')
        user = parser.get(tries, 'user')
        password = parser.get(tries, 'pass')
        if database is None:
            database = parser.get(tries, 'database')
        encoding = parser.get(tries, 'encoding')

        try:
            log.debug(f"{tries} section을 통하여 로그인을 시도합니다.")
            connection = pymysql.connect(host=host, user=user, password=password, db=database, charset=encoding)
        except pymysql.err.OperationalError:
            continue
        return connection
