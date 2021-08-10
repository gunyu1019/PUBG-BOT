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
    client_list = cur.fetchone()

token = client_list.get('token')
PUBG_API = client_list.get('PUBG_API')

# Discord Bot Lists API TOKEN
DBL_token = client_list.get('topgg_token')
koreanBots_token = client_list.get('KoreanBots_token')
uniqueBots_token = client_list.get('UniqueBots_token')

connect.close()
