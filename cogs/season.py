import datetime
import logging
import pymysql
import json

from discord.ext import tasks, commands

from utils.database import getDatabase
from utils.request import requests, platform_site

log = logging.getLogger(__name__)


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.check_season.start()

    @tasks.loop(minutes=120)
    async def check_season(self):
        time_now = datetime.datetime.now()
        connect = getDatabase()

        cur = connect.cursor()
        sql = "SELECT last_update, Steam FROM SEASON_STATUS"
        cur.execute(sql)
        cache = cur.fetchone()
        last_update = cache[0]
        html1 = cache[1]

        date_json1 = json.loads(last_update)
        date_json2 = json.loads(html1)
        time_last = datetime.datetime(date_json1['years'], date_json1['months'], date_json1['days'],
                                      date_json1['hours'], date_json1['minutes'])
        time_delta = time_now - time_last
        if time_delta.days > 2:
            log.info('시즌정보를 체크합니다.')
            response = await requests("GET", "https://api.pubg.com/shards/steam/seasons")
            if response.status_code == 200:
                html2 = [None] * 5
                html2[0] = response.json()
                if date_json2 != html2:
                    c = 1
                    for i in platform_site[1:]:
                        response = await requests("GET", f"https://api.pubg.com/shards/{i}/seasons")
                        html2[c] = response.json()
                        c += 1
                    steam_s = json.dumps(html2[0], indent=2)
                    kakao_s = json.dumps(html2[1], indent=2)
                    xbox_s = json.dumps(html2[2], indent=2)
                    psn_s = json.dumps(html2[3], indent=2)
                    stadia_s = json.dumps(html2[4], indent=2)
                    log.info('시즌 정보가 변경되었습니다.')
                    w_time = {
                        "years": time_now.year,
                        "months": time_now.month,
                        "days": time_now.day,
                        "hours": time_now.hour,
                        "minutes": time_now.minute
                    }
                    sql = pymysql.escape_string('UPDATE SEASON_STATUS SET Steam=%s,Kakao=%s,XBOX=%s,psn=%s,Stadia=%s,last_update=%s WHERE id=1')
                    cur.execute(sql, (steam_s, kakao_s, xbox_s, psn_s, stadia_s, json.dumps(w_time)))
            else:
                log.warning(f"시즌 업데이트에 실패하였습니다: response 에러 (%s): %s" % (response.status, response.data))
        connect.commit()
        connect.close()

    @check_season.before_loop
    async def before_booting(self):
        await self.bot.wait_until_ready()


def setup(client):
    client.add_cog(Task(client))
