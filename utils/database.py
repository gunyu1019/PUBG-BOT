import pymysql
import logging
from config.config import parser

log = logging.getLogger(__name__)


def getDatabase(database=None):
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
