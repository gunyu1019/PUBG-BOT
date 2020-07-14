import requests_async as requests
import pymysql
import os
import sys
import platform
import json
import datetime

if platform.system() == "Windows":
    type_software = '\\'
elif platform.system() == "Linux":
    type_software = '/'
directory = os.path.dirname(os.path.abspath(__file__)).replace(type_software + "modules","")
db_f = open(directory + type_software + "data" + type_software + "bot_info.json",mode='r')
db = db_f.read()
db_f.close()
db_json = json.loads(db)

db_ip = db_json["mysql"]["ip"]
db_user = db_json["mysql"]["user"]
db_pw = db_json["mysql"]["password"]
db_name = db_json["mysql"]["database"]

class player:
    def __init__(self, player_id):
        self.player_id = player_id

    async def lastupdate(self,pubg_type):
        player_id = self.player_id
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect.cursor()
        sql = "select last_update from player where id=%s"
        cur.execute(sql,(str(player_id)))
        cache = cur.fetchall()
        time = cache[0][0]
        connect.close()
        date_json = json.loads(time)[str(pubg_type)]
        return datetime.datetime(date_json["years"],date_json["months"],date_json["days"],hour=date_json["hours"],minute=date_json["minutes"])

    async def autopost(self,pubg_type):
        first = await self.lastupdate(pubg_type)
        second = datetime.datetime.now()
        delta = second - first
        if delta.days >= 2:
            return True
        return False
        
    async def lastupdate_insert(self,pubg_type,player_datetime):
        player_id = self.player_id
        years = player_datetime.year #분별
        months = player_datetime.month
        days = player_datetime.day
        hours = player_datetime.hour
        minutes = player_datetime.minute
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8') #업데이트값 가져오기
        cur = connect.cursor()
        sql = "select last_update from player where id=%s"
        cur.execute(sql,(str(player_id)))
        cache = cur.fetchall()
        date = cache[0][0]
        date_json = json.loads(date)
        date_json[pubg_type]["years"] = years #값 반영파트
        date_json[pubg_type]["months"] = months
        date_json[pubg_type]["days"] = days
        date_json[pubg_type]["hours"] = hours
        date_json[pubg_type]["minutes"] = minutes
        sql = "UPDATE player SET last_update=%s WHERE id=%s"
        cur.execute(sql,(json.dumps(date_json),str(player_id)))
        connect.commit()
        connect.close()
        return

    async def name(self):
        player_id = self.player_id
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect.cursor()
        sql = "select name from player where id=%s"
        cur.execute(sql,(str(player_id)))
        cache = cur.fetchall()
        player_name = cache[0][0]
        connect.close()
        return player_name