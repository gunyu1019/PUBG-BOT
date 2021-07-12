import pymysql

from utils.database import getDatabase

connect = getDatabase()

cur = connect.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT * from PUBG_BOT")

client_list = cur.fetchone()
DBL_token = client_list['DBL_token']
token = client_list['token']
DBKR_token = client_list['DBKR_token']
PUBG_API = client_list['DB_token']

connect.close()
