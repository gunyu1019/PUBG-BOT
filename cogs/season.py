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

import logging
import pymysql
import json

from discord.ext import tasks, commands

from module.pubgpy import Api, Platforms, APIException
from utils.database import get_database
from utils.token import PUBG_API

log = logging.getLogger(__name__)
platform_site = [i for i in Platforms]


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.check_season.start()
        self.requests = Api(token=PUBG_API)

    @tasks.loop(minutes=120)
    async def check_season(self):
        time_now = datetime.datetime.now()
        connect = get_database()

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
            self.requests.platform = platform_site[0].value
            try:
                response = await self.requests.requests("GET", "/seasons")
            except APIException as message:
                log.warning(f"시즌 업데이트에 실패하였습니다: response 에러 %s" % message)
            else:
                html2 = [None, None, None, None, None]
                html2[0] = response
                if date_json2 != html2:
                    c = 1
                    for i in platform_site[1:]:
                        self.requests.platform = i.value
                        html2[c] = await self.requests.requests("GET", "/seasons")
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
        connect.commit()
        connect.close()

    @check_season.before_loop
    async def before_booting(self):
        await self.bot.wait_until_ready()


def setup(client):
    client.add_cog(Task(client))
