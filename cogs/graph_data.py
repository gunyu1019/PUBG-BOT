import logging
import datetime
import pymysql
import aiohttp

from discord.ext import tasks, commands

from utils.database import get_database

log = logging.getLogger(__name__)


class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.check_player.start()

    @staticmethod
    async def requests(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = {
                    "text": await resp.text(),
                    "status_code": resp.status
                }
        return result

    @tasks.loop(minutes=10)
    async def check_player(self):
        time_now = datetime.datetime.now()
        connect = get_database()
        cur = connect.cursor()

        sql_v2_ck = "SELECT date FROM SERVER_DATA WHERE ID=12"
        cur.execute(sql_v2_ck)
        lasted_update = cur.fetchone()[0]
        if (time_now - lasted_update).seconds >= 3600:
            response = await self.requests("https://steamcommunity.com/app/578080")
            if response['status_code'] == 200:
                html = response['text']
                players = html.split('<span class="apphub_NumInApp">')[1].split('</span>')[0]
                players = players.replace("In-Game", "").replace(" ", "").replace(",", "")
                for i in range(12):
                    sql_v2_ps = "UPDATE SERVER_DATA SET id=%s WHERE id=%s"
                    cur.execute(sql_v2_ps, (i, i + 1))
                sql_v2_pd = "DELETE FROM SERVER_DATA WHERE ID=0"
                sql_v2_pc = pymysql.escape_string("INSERT INTO SERVER_DATA(data, date, id) VALUES(%s, %s, 12)")
                cur.execute(sql_v2_pd)
                cur.execute(sql_v2_pc, (int(players), time_now.strftime('%Y-%m-%d %H:%M:%S')))
                logging.info("그래프에 반영합니다. 시간 " + time_now.strftime('%H:%M') + ",유저수: " + str(players) + "명")
            else:
                logging.info("그래프에 반영을 실패했습니다. 시간 " + time_now.strftime('%H:%M'))
        connect.commit()
        connect.close()

    @check_player.before_loop
    async def before_booting(self):
        await self.bot.wait_until_ready()


def setup(client):
    client.add_cog(Task(client))
