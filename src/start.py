import discord
import asyncio
import os
import sys
import datetime
import time
import platform
import pymysql
import io
#import csv
import requests_async as requests
import json
import psutil

import dbl
import dbkrpy

from matplotlib import pyplot as plt
from pytz import timezone

image_name = ["steam.png","kakao.png","xbox.png","playstation.png","stadia.png"]
platform_name = ["Steam","Kakao","XBOX","PS","Stadia"]
platform_site = ["steam","kakao","xbox","psn","stadia"]

xbox = "<:XBOX:718482204035907586>"
playstation = "<:PS:718482204417720400>"
steam = "<:Steam:698454004656504852>"
kakao = "<:kakao:718482204103278622>"
stadia = "<:Stadia:718482205575348264>"
version = "v1.1.1(2020-10-27)"

def image(pubg_platform):
    kakao = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "kakao.png")
    steam = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "steam.png")
    xbox = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "xbox.png")
    playstation = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "playstation.png")
    stadia = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "stadia.png")
    image = [steam,kakao,xbox,playstation,stadia]
    return image[pubg_platform]

def is_manager(user_id):
    if platform.system() == "Windows":
        file = open(directory + "\\user_info\\Manager.txt",mode='r')
    elif platform.system() == "Linux":
        file = open(directory + "/user_info/Manager.txt",mode='r')
    else:
        return False
    cache1 = file.readlines()
    file.close()
    if user_id in cache1:
    	return True
    return False

def is_admin(message):
    for role in message.author.roles:
        if role.permissions.administrator:
            return True
    return False 

def is_banned(user_id,message):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect .cursor()
    sql_prefix = "select * from BLACKLIST"
    cur.execute(sql_prefix)
    banned_list = cur.fetchall()
    connect.close()
    for banned in banned_list:
        print(banned[0])
        if banned[0] == int(user_id):
            if message.content[1:].startswith("블랙리스트 여부"):
                log_info(message.guild.name,message.channel,str(message.author),str(message.author) + '잘못된 유저가 접근하고 있습니다!(' + message.content + ')')
                embed = discord.Embed(title="권한 거부(403)", color=0x00aaaa)
                embed.add_field(name="권한이 거부되었습니다.", value="당신은 블랙리스트로 등록되어 있습니다.", inline=False)
                coro = message.channel.send(embed=embed)
                asyncio.run_coroutine_threadsafe(coro, client.loop)
            return True
    return False

def log_info(guild, channel, user, message):
    Ftime = time.strftime('%Y-%m-%d %p %I:%M:%S', time.localtime(time.time()))
    print("[시간: " + str(Ftime) + " | " + str(guild) + " | " + str(channel) + " | " + str(user) + "]: " + str(message))
    log = open(f"{directory}/log/message.txt","a",encoding = 'utf-8')
    log.write("[시간: " + str(Ftime) + " | " + str(guild) + " | " + str(channel) + " | " + str(user) + "]: " + str(message) + "\n")
    log.close()
    #log_info(message.guild,message.channel,message.author,message.content)

def log_system(message):
    r_time = time.strftime('%Y-%m-%d %p %I:%M:%S', time.localtime(time.time()))
    print(f"[{r_time}]: {message}")
    log = open(f"{directory}/log/system.txt","a",encoding = 'utf-8')
    log.write(f"[{r_time}]: {message}\n")
    log.close()

def log_error(message):
    r_time = time.strftime('%Y-%m-%d %p %I:%M:%S', time.localtime(time.time()))
    print(f"[{r_time}]: {message}")
    log = open(f"{directory}/log/error.txt","a",encoding = 'utf-8')
    log.write(f"[{r_time}]: {message}\n")
    log.close()

#쓸때없는거(?)같은 괜찮은거
def change_data(B):
    B_lens = len(str(B))
    if B_lens >= 17:
        return round(B/1000000000000000,2), "PB"
    elif B_lens  >= 13:
        return round(B/1000000000000,2), "TB"
    elif B_lens >= 10:
        return round(B/1000000000,2), "GB"
    elif B_lens >= 7:
        return round(B/1000000,2), "MB"
    elif B_lens >= 4:
        return round(B/1000,2), "KB"
    return round(B,2), "B"

#자동업데이트가 필요한 함수들입니다. autopost1, autopost2, autopost3
async def autopost1():
    await client.wait_until_ready()
    while not client.is_closed():
        await client.change_presence(status=discord.Status.online, activity=discord.Game("[접두어]help, [접두어]도움말 를 이용하여, 명령어를 알아보세요!"))
        await asyncio.sleep(3.0)
        total = 0
        for i in range(len(client.guilds)):
            total += len(client.guilds[i].members)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("활동중인 서버갯수: " + str(len(client.guilds)) + "개, 유저수" + str(total) + "명"))
        await asyncio.sleep(3.0)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("PUBG봇은 현재 OBT를 시행중입니다. 오류 발생시 신고해주시기 바랍니다."))
        await asyncio.sleep(3.0)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("접두어를 잊어먹을 경우 !=접두어 정보를 통하여 얻을수 있습니다!"))
        await asyncio.sleep(3.0)

async def autopost2(time):
    a_time = int(time) * 60
    await client.wait_until_ready()
    while not client.is_closed():
        response = await requests.get("https://steamcommunity.com/app/578080")
        if response.status_code == 200:
            html = response.text
            players = html.split('<span class="apphub_NumInApp">')[1].split('</span>')[0]
            players = players.replace("In-Game","").replace(" ","").replace(",","")
            global DB_players
            for i in range(len(DB_players)-1):
                DB_players[i] = DB_players[i+1]
                DB_datetime[i] = DB_datetime[i+1]
            DB_players[len(DB_players)-1] = int(players)
            DB_datetime[len(DB_players)-1] = datetime.datetime.now().strftime('%H:%M')
            print("그래프에 반영합니다. 시간" + datetime.datetime.now().strftime('%H:%M') + ",유저수: " + str(players) + "명")
        else:
            print("그래프에 반영을 실패했습니다. 시간" + datetime.datetime.now().strftime('%H:%M'))
        await asyncio.sleep(a_time)

async def autopost3():
    await client.wait_until_ready()
    while not client.is_closed():
        time_now = datetime.datetime.now()
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db='PUBG_BOT', charset='utf8')
        try:
            cur = connect.cursor()
            sql = f"SELECT last_update, html FROM SEASON"
            cur.execute(sql)
            cache = cur.fetchone()
            last_update = cache[0]
            html1 = cache[1]
        except:
            raise
        date_json1 = json.loads(last_update)
        date_json2 = json.loads(html1)
        time_last = datetime.datetime(date_json1['years'],date_json1['months'],date_json1['days'],date_json1['hours'],date_json1['minutes'])
        time_delta = time_now - time_last
        if time_delta.days > 2:
            log_system('시즌정보를 체크합니다.')
            response = await requests.get("https://api.pubg.com/shards/steam/seasons",headers=header)
            if response.status_code == 200:
                html2 = response.json()
                if date_json2 != html2:
                    log_system('시즌 정보가 변경되었습니다.')
                    w_time = {
                        "years":time_now.year,
                        "months":time_now.month,
                        "days":time_now.day,
                        "hours":time_now.hour,
                        "minutes":time_now.minute
                    }
                    sql = 'UPDATE SEASON SET html=%s,last_update=%s WHERE id=1'
                    cur.execute(sql,(json.dumps(html2),json.dumps(w_time)))
            else:
                print(response.status_code,response.json())
        connect.commit()
        connect.close()
        await asyncio.sleep(120.0)

def time_num(playtime): #시간 계산, 불필요한 월단위, 일단위 등의 제거
    if playtime.month == 1:
        if playtime.day == 1:
            if playtime.hour == 0:
                if  playtime.minute == 0:
                    return str(playtime.second)  + "초"
                return str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
            return str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
        return str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
    return str(playtime.month-1)  + "일 " + str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"

async def response_num(response,message): #에러 발생시, 코드를 통하여 분석
    a_num = int(response.status_code)
    if a_num == 200:
        return
    elif a_num == 400:
        embed = discord.Embed(title="에러",description="닉네임을 입력해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 401:
        embed = discord.Embed(title="에러",description="DB 불러오는것을 실패하였습니다. 잠시후 다시시도 해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 404:
        embed = discord.Embed(title="에러",description="해당 유저를 찾을수 없습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 415:
        embed = discord.Embed(title="에러",description="콘텐츠 지정이 잘못되었습니다. 봇 제작자에게 문의해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 429:
        embed = discord.Embed(title="에러",description="너무 많은 요청이 들어왔습니다. 잠시후 다시시도해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    embed = discord.Embed(title="에러",description="알수없는 에러가 발생하였습니다. 관리자에게 문의해주세요.", color=0xaa0000)
    await message.channel.send(embed=embed)
    return

if platform.system() == "Windows":
    type_software = '\\'
elif platform.system() == "Linux":
    type_software = '/'
directory = os.path.dirname(os.path.abspath(__file__))
db_f = open(directory + type_software + "data" + type_software + "bot_info.json",mode='r')
db = db_f.read()
db_f.close()
db_json = json.loads(db)

db_ip = db_json["mysql"]["ip"]
db_user = db_json["mysql"]["user"]
db_pw = db_json["mysql"]["password"]
db_name = db_json["mysql"]["database"]

sys.path.append(directory + type_software + "modules") #다른 파일내 함수추가
import player as p_info
import status as s_info
import matches_status as m_info
import normal
import ranked
import matches

map_link_f = open(directory + type_software + "data" + type_software + "map_link.json",mode='r')
map_link_r = map_link_f.read()
map_link_f.close()
map_link = json.loads(map_link_r)

connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8') #클라이언트 API키 불러오기.
cur = connect.cursor()
cur.execute("SELECT * from PUBG_BOT")
client_list = cur.fetchall()
token = client_list[0][0]
pubg_token = client_list[0][2]
DBL_token = client_list[0][1]
DBKR_token = client_list[0][3]
connect.close()

client = discord.Client()
header = {
  "Authorization": "Bearer " + pubg_token,
  "Accept": "application/vnd.api+json"
}

sample1 = { #마지막업데이트값의 샘플값입니다.
  "weapon":{
    "years":1,
    "months":1,
    "days":1,
    "hours":0,
    "minutes":0
  },
  "matches":{
    "years":1,
    "months":1,
    "days":1,
    "hours":0,
    "minutes":0
  },
  "normal":{
    "years":1,
    "months":1,
    "days":1,
    "hours":0,
    "minutes":0
  },
  "ranked":{
    "years":1,
    "months":1,
    "days":1,
    "hours":0,
    "minutes":0
  }
}

DB_players = [0] * 12
DB_datetime = ["starting"] * 12

DBL = None
DBKR = None

async def player(nickname,message,pubg_platform):
    response = await requests.get("https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players?filter[playerNames]=" + nickname, headers=header)
    if response.status_code == 200:
        json_data = response.json()
    else:
        await response_num(response, message)
        return "Failed_Response"
    return json_data["data"][0]["id"]

async def player_info(message,nickname):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    try:
        sql = "select id,platform from player where name=%s"
        cur.execute(sql,(str(nickname)))
        cache = cur.fetchall()
        pubg_id = cache[0][0]
        pubg_platform = cache[0][1]
    except Exception:
        embed = discord.Embed(title="플랫폼 선택!",description="해당 계정의 플랫폼을 선택해주세요.\n유저를 처음 검색 했을 때 뜨는 기능이며, \U0000274C를 통해 취소 가능합니다.", color=0xffd619)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction(steam)
        await msg.add_reaction(kakao)
        await msg.add_reaction(xbox)
        await msg.add_reaction(playstation)
        await msg.add_reaction(stadia)
        await msg.add_reaction("\U0000274C")
        emoji = [steam,kakao,xbox,playstation,stadia,"\U0000274C"]
        def check2(reaction,user):
            for i in range(5):
                if str(reaction.emoji)==str(emoji[i]):
                    return user == message.author
        try:
            reaction,_ = await client.wait_for('reaction_add',check=check2,timeout=20)
        except asyncio.TimeoutError:
            await msg.delete()
            embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다! 20초 내로 선택해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
        await msg.delete()
        count = 0
        if reaction.emoji == "\U0000274C":
            return "Failed_Response", 0
        for i in range(5):
            if str(reaction.emoji)==str(emoji[i]):
                count = i
        pubg_platform = count
        pubg_id = await player(nickname,message,count)
        if pubg_id == "Failed_Response":
            return "Failed_Response", pubg_platform
        sql = """insert into player(id,name,last_update,platform)
                values (%s, %s, %s, %s)"""
        cur.execute(sql, (pubg_id,nickname,json.dumps(sample1),count))
        connect.commit()
    finally:
        connect.close()
    return pubg_id, pubg_platform

async def profile(message,prefix,command):
    list_message = message.content.split(" ")
    nickname = ""
    if command == "Information":
        pubg_type_all = ['1인칭','3인칭','일반','랭크']
        helper = "**" + prefix + "전적[솔로|듀오(경쟁 X)|스쿼드] [1인칭|3인칭 혹은 일반|3인칭경쟁 혹은 경쟁, 랭크|1인칭경쟁] [닉네임(선택)] [시즌(선택)]**:"
        try:
            pubg_type = list_message[1]
            if not pubg_type in pubg_type_all:
                embed = discord.Embed(title="에러",description=helper + " 1인칭, 3인칭 혹은 일반, 랭크 중에서만 선택하여 주세요.", color=0xaa0000)
                await message.channel.send(embed=embed)
                return
        except Exception:
            embed = discord.Embed(title="에러",description=helper + " 1인칭, 3인칭 혹은 일반, 랭크 중에서 선택하여 주세요.", color=0xaa0000)
            await message.channel.send(embed=embed)
            return
    try:
        if command == "Information":
            nickname = list_message[2]
        else:
            nickname = list_message[1]
    except Exception:
        embed = discord.Embed(title="닉네임 작성 요청!",description="닉네임을 작성해주세요!\n취소를 하고싶으시다면 \"" + prefix + "취소\"를 적어주세요.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check1(m):
            return message.author.id == m.author.id and message.channel.id == m.channel.id
        try:
            a_nickname = await client.wait_for('message',check=check1,timeout=20)
            nickname = a_nickname.content
            if nickname == prefix + "취소":
                await msg1.delete()
                return
            await msg1.delete()
        except asyncio.TimeoutError:
            await msg1.delete()
            embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다! 20초 내로 선택해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            return
    pubg_id,pubg_platform = await player_info(message,nickname)
    if pubg_id == "Failed_Response":
        return
    if command == "Information":
        try:
            s_count = list_message[3]
            if len(s_count) < 2:
                season = "division.bro.official.pc-2018-0" + s_count
            else:
                season = "division.bro.official.pc-2018-" + s_count
        except Exception:
            connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db='PUBG_BOT', charset='utf8')
            try:
                cur = connect.cursor()
                sql = f"SELECT html FROM SEASON"
                cur.execute(sql)
                cache = cur.fetchone()
                html = cache[0]
            except:
                raise
            data_json = json.loads(html)['data']
            least_season = data_json[len(data_json)-1]
            season = least_season['id']
        if pubg_type == "랭크" or pubg_type == "3인칭경쟁" or pubg_type == "경쟁":
            pubg_json = await s_info.ranked_status(pubg_id,season,message,pubg_platform)
            if list_message[0] == prefix + "전적":
                await ranked.ranked_total(message,client,pubg_platform,"tpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적솔로":
                await ranked.ranked_mode(message,client,pubg_platform,"tpp","solo",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적스쿼드":
                await ranked.ranked_mode(message,client,pubg_platform,"tpp","squad",pubg_json,season,pubg_id)
            return
        elif pubg_type == "1인칭경쟁":
            pubg_json = await s_info.ranked_status(pubg_id,season,message,pubg_platform)
            if list_message[0] == prefix + "전적":
                await ranked.ranked_total(message,client,pubg_platform,"fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적솔로":
                await ranked.ranked_mode(message,client,pubg_platform,"fpp","solo-fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적스쿼드":
                await ranked.ranked_mode(message,client,pubg_platform,"fpp","squad-fpp",pubg_json,season,pubg_id)
            return
        elif pubg_type == "1인칭":
            pubg_json = await s_info.season_status(pubg_id,season,message,pubg_platform)
            if pubg_json == "Failed_Response":
                return
            if list_message[0] == prefix + "전적":
                await normal.profile_total(message,client,pubg_platform,"fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적솔로":
                await normal.profile_mode(message,client,pubg_platform,"fpp","solo-fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적듀오":
                await normal.profile_mode(message,client,pubg_platform,"fpp","duo-fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적스쿼드":
                await normal.profile_mode(message,client,pubg_platform,"fpp","squad-fpp",pubg_json,season,pubg_id)
            return
        elif pubg_type == "일반" or pubg_type == "3인칭":
            pubg_json = await s_info.season_status(pubg_id,season,message,pubg_platform)
            if pubg_json == "Failed_Response":
                return
            if list_message[0] == prefix + "전적":
                await normal.profile_total(message,client,pubg_platform,"fpp",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적솔로":
                await normal.profile_mode(message,client,pubg_platform,"tpp","solo",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적듀오":
                await normal.profile_mode(message,client,pubg_platform,"tpp","duo",pubg_json,season,pubg_id)
            elif list_message[0] == prefix + "전적스쿼드":
                await normal.profile_mode(message,client,pubg_platform,"tpp","squad",pubg_json,season,pubg_id)
            return
        embed = discord.Embed(title="에러",description=helper + " 1인칭,3인칭,일반,랭크 중에서 골라주세요. 일반 그리고 3인칭과는 같은 기능입니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif command == "Matches":
        embed = discord.Embed(title="PUBG",description="최근 검색하실 전적을 고르시기 바랍니다.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check2(reaction,user):
            for i in range(5):
                if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                    return user.id == message.author.id and msg1.id==reaction.message.id
        for i in range(5):
            await msg1.add_reaction(str(i+1) +  "\U0000FE0F\U000020E3")
        reaction,_ = await client.wait_for('reaction_add', check=check2)
        count = None
        for i in range(5):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                count = i
                break
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed = discord.Embed(title="\U000026A0경고!",description="디스코드봇에게 \"메세지 관리\"권한을 부여해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
        pubg_json = await m_info.match_status(pubg_id,message,pubg_platform)
        if pubg_json == "Failed_Response":
            return
        await msg1.delete()
        await matches.get(message,client,pubg_json,pubg_id,count,pubg_platform)
        return

async def platform_exchange(message,prefix):
    list_message = message.content.split()
    try:
        nickname = list_message[1]
    except Exception:
        embed = discord.Embed(title="닉네임 작성 요청!",description="닉네임을 작성해주세요!\n취소를 하고싶으시다면 \"" + prefix + "취소\"를 적어주세요.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check1(m):
            return message.author.id == m.author.id and message.channel.id == m.channel.id
        try:
            a_nickname = await client.wait_for('message',check=check1,timeout=20)
            nickname = a_nickname.content
            if nickname == prefix + "취소":
                await msg1.delete()
                return
            await msg1.delete()
        except asyncio.TimeoutError:
            await msg1.delete()
            embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다! 20초 내로 선택해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            return
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    try:
        sql = "select id from player where name=%s"
        cur.execute(sql,(str(nickname)))
        cache = cur.fetchone()
        pubg_id = cache[0]
    except:
        embed = discord.Embed(title="에러!",description="해당 유저가 등록되어 있지 않습니다. 최초 1회 이상 조회해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    embed = discord.Embed(title="플랫폼 변경",description="해당 계정의 플랫폼을 선택해주세요.\n잘못 사용했을 경우 \U0000274C를 통해 취소 가능합니다.", color=0xffd619)
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction(steam)
    await msg.add_reaction(kakao)
    await msg.add_reaction(xbox)
    await msg.add_reaction(playstation)
    await msg.add_reaction(stadia)
    await msg.add_reaction("\U0000274C")
    emoji = [steam,kakao,xbox,playstation,stadia,"\U0000274C"]
    def check3(reaction,user):
        for i in range(5):
            if str(reaction.emoji)==str(emoji[i]):
                return user == message.author
    try:
        reaction,_ = await client.wait_for('reaction_add',check=check3,timeout=20)
    except asyncio.TimeoutError:
        await msg.delete()
        embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다! 20초 내로 선택해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        await msg.delete()
    count = 0
    if reaction.emoji == "\U0000274C":
        return
    for i in range(5):
        if str(reaction.emoji)==str(emoji[i]):
            count = i
    await msg.delete()
    embed = discord.Embed(title="플랫폼 변경",description="성공적으로 플랫폼 변경이 되었습니다.", color=0xffd619)
    await message.channel.send(embed=embed)
    pubg_platform = count
    sql = pymysql.escape_string("UPDATE player SET platform=%s WHERE=%s",pubg_platform,pubg_id)
    cur.execute(sql)
    connect.commit()
    connect.close()
    return

@client.event
async def on_ready():
    log_system('디스코드 봇 로그인이 완료되었습니다.')
    log_system("디스코드봇 이름:" + client.user.name)
    log_system("디스코드봇 ID:" + str(client.user.id))
    log_system("디스코드봇 버전:" + str(discord.__version__))
    print('------------')
    answer = ""
    total = 0
    for i in range(len(client.guilds)):
        answer = answer + str(i+1) + "번째: " + str(client.guilds[i]) + "(" + str(client.guilds[i].id) + "):"+ str(len(client.guilds[i].members)) +"명\n"
        total += len(client.guilds[i].members)
    log_system("방목록: \n" + answer + "방의 종합 멤버:" + str(total) + "명")
    global DBL, DBKR
    DBL = dbl.DBLClient(client,DBL_token,autopost=True)
    DBKR = dbkrpy.UpdateGuilds(client,DBKR_token)

@client.event
async def on_message(message):
    author_id = message.author.mention.replace("<@","",).replace(">","").replace("!","")
    list_message = message.content.split(' ')
    if message.author == client.user or message.author.bot:
        return
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    try:
        cur = connect .cursor()
        sql_prefix = pymysql.escape_string("select * from SERVER_INFO where ID=%s",message.guild.id)
        cur.execute(sql_prefix)
        cache = cur.fetchall()
        prefix = cache[0][1]
    except Exception:
        prefix = "!="
    connect.close()
    if message.content.startswith(prefix + '전적'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        await profile(message,prefix,'Information')
        return
    if message.content.startswith(prefix + '매치'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        await profile(message,prefix,'Matches')
        return
    if message.content.startswith(prefix + '접두어') or message.content.startswith('!=접두어') :
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        if message.guild == None:
            embed = discord.Embed(title="접두어",description="DM에서는 접두어 기능을 사용하실수 없습니다.", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        try:
            mode = list_message[1]
        except Exception:
            if prefix == "=":
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
            else:
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + prefix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        else:
            connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
            cur = connect .cursor()
            if mode == "설정":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                try:
                    n_prefix = list_message[2]
                    if len(n_prefix) > 4 or len(list_message) > 3 or n_prefix.find('\t') != -1 or n_prefix.find('\n') != -1 :
                        if prefix == "=":
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                        else:
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + prefix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                        await message.channel.send(embed=embed)
                        connect.close()
                        return
                except Exception:
                    if prefix == "=":
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                    else:
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + prefix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.commit()
                    connect.close()
                    return
                sql_T = pymysql.escape_string("select EXISTS (select * from SERVER_INFO where ID=%s) as success",message.guild.id)
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    sql = "insert into SERVER_INFO(ID,PERFIX) values (%s, %s)"
                    cur.execute(sql,(message.guild.id,n_prefix))
                else:
                    sql = pymysql.escape_string("update SERVER_INFO set PERFIX=%s where ID=%s",n_prefix,message.guild.id)
                    cur.execute(sql)
                embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + n_prefix + "(명령어)으로 성공적으로 설정되었습니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.commit()
                connect.close()
            elif mode == "초기화":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                sql_T = pymysql.escape_string("select EXISTS (select * from SERVER_INFO where ID=%s) as success",message.guild.id)
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    embed = discord.Embed(title="접두어",description="접두어가 이미 기본설정(!=)으로 되어 있습니다...", color=0xffd619)
                else:
                    sql = pymysql.escape_string("update SERVER_INFO set PERFIX='!=' where ID=%s",message.guild.id)
                    cur.execute(sql)
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)으로 성공적으로 초기화가 완료되었습니다.", color=0xffd619)
                    connect.commit()
                connect.close()
                await message.channel.send(embed=embed)
            elif mode == "정보":
                try:
                    sql_prefix = pymysql.escape_string("select * from SERVER_INFO where ID=",message.guild.id)
                    cur.execute(sql_prefix)
                    c_prefix = cur.fetchall()
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + str(c_prefix[0][1]) + "(명령어)입니다.", color=0xffd619)
                except Exception:
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)입니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.close()
                return
            else:
                if prefix == "=":
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                else:
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + prefix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                connect.close()
                await message.channel.send(embed=embed)
                return
    if message.content == prefix + "도움" or message.content == prefix + "도움말" or message.content == prefix + "help":
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        async def help_command(help_page):
            embed = discord.Embed(title="도움말",color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
            if help_page == 1:
                embed.add_field(name=prefix + "전적 [1인칭|3인칭 혹은 일반|3인칭경쟁 혹은 경쟁, 랭크|1인칭경쟁] [닉네임(선택)] [시즌(선택)]:",value="배틀그라운드 종합 전적을 검색해 줍니다.",inline=False)
                embed.add_field(name=prefix + "전적[솔로|듀오(경쟁 X)|스쿼드] [1인칭|3인칭 혹은 일반|3인칭경쟁 혹은 경쟁, 랭크|1인칭경쟁] [닉네임(선택)] [시즌(선택)]:",value="배틀그라운드 솔로/듀오/스쿼드 모드에 대한 전적을 검색해 줍니다.",inline=False)
                embed.add_field(name=prefix + "매치 [닉네임]:",value="해당 유저에 대한 매치 전적을 확일 할수 있게 해줍니다.",inline=False)
                embed.add_field(name=prefix + "서버상태:",value="배틀그라운드 서버 상태를 알려줍니다.",inline=False)
                embed.add_field(name=prefix + "플랫폼변경 [닉네임]:",value="유저 플랫폼을 잘못 등록했을 경우 변경 기능을 제공합니다.",inline=False)
            elif help_page == 2:
                embed.add_field(name=prefix + "에란겔:",value="배틀그라운드 에란겔 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "미라마:",value="배틀그라운드 미라마 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "사녹:",value="배틀그라운드 사녹 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "비켄디:",value="배틀그라운드 비켄디 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "카라킨:",value="배틀그라운드 카라킨 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "카라킨:",value="배틀그라운드 파라모 맵에 대해 볼 수 있습니다.",inline=False)
                embed.add_field(name=prefix + "캠프자칼:",value="배틀그라운드 캠프자칼 맵에 대해 볼 수 있습니다.",inline=False)
            elif help_page == 3:
                embed.add_field(name=prefix + "ping:",value="디스코드봇의 ping을 알려줍니다.",inline=False)
                embed.add_field(name=prefix + "정보:",value="디스코드봇의 정보를 알려줍니다.",inline=False)
                embed.add_field(name=prefix + "접두어 [설정/초기화/정보] [(설정 사용시)설정할 접두어]:",value="접두어를 설정합니다.",inline=False)
                embed.add_field(name=prefix + "블랙리스트 [추가/여부/제거] [맨션(선택)]:", value="해당 기능을 통해 유저가 PUBG BOT를 사용하지 못하도록 설정할수 있습니다.",inline=False)
            embed.set_footer(text=f"{version} | 페이지: {help_page}/3")
            msg = await message.channel.send(embed=embed)
            if not help_page == 1:
                await msg.add_reaction("\U00002B05")
            if not help_page == 3:
                await msg.add_reaction("\U000027A1")
            message_id = msg.id
            def check(reaction, user):
                if "\U000027A1" == reaction.emoji or "\U00002B05" == reaction.emoji:
                    return user.id == message.author.id and message_id == reaction.message.id
            reaction,_ = await client.wait_for('reaction_add', check=check)
            if reaction.emoji == "\U000027A1":
                await msg.delete()
                await help_command(help_page+1)
            elif reaction.emoji == "\U00002B05":
                await msg.delete()
                await help_command(help_page-1)
            return
        await help_command(1)
        return
    if message.content.startswith(f'{prefix}플랫폼변경'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        await platform_exchange(message,prefix)
        return
    if message.content == prefix + "서버상태":
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        response = await requests.get("https://steamcommunity.com/app/578080")
        if response.status_code == 200:
            html = response.text
        else:
            embed = discord.Embed(title="에러",description=message.guild.name + "정보를 불러오기에 실패했습니다..", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        plt.clf()
        plt.title('Max Players')
        plt.plot(DB_datetime,DB_players,color='blue', marker='o',label = 'Max Players')
        plt.xlabel('time')
        plt.ylabel('user')
        print("그래프 만들기 성공!")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = discord.File(buf,filename="cache.png")
        players = html.split('<span class="apphub_NumInApp">')[1].split('</span>')[0].replace("In-Game","").replace(" ","")
        embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
        embed.add_field(name="서버상태:",value="정상",inline=True)
        embed.add_field(name="동접자수:",value=players + "명 유저가 플레이 중입니다.",inline=True)
        embed.set_image(url="attachment://cache.png")
        await message.channel.send(file=file,embed=embed)
        return
    if message.content.startswith(prefix + 'eval') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        code =  message.content.replace(prefix + 'eval ','')
        if code == "" or code == prefix + "eval":
            embed = discord.Embed(title="에러!",description="내용을 적어주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        try:
            answer = eval(code)
        except Exception as e:
            embed = discord.Embed(title="eval",description=f'작동중에 에러가 발생하였습니다.\n```{e}```', color=0xffd619)
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="eval",description=answer, color=0xffd619)
        await message.channel.send(embed=embed)
        return
    if message.content == prefix + "ping" or message.content == prefix + "핑" :
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        now = datetime.datetime.utcnow()
        response_ping_c = now - message.created_at
        reading_ping = float(f"{response_ping_c.seconds}.{response_ping_c.microseconds}")
        embed = discord.Embed(title="Pong!",description=f"클라이언트 핑상태: {round(client.latency * 1000,2)}ms\n읽기 속도: {round(reading_ping * 1000,2)}ms", color=0xffd619)
        msg = await message.channel.send(embed=embed)
        now = datetime.datetime.utcnow()
        response_ping_a = now - msg.created_at
        response_ping = float(f"{response_ping_a.seconds}.{response_ping_a.microseconds}")
        embed = discord.Embed(title="Pong!",description=f"클라이언트 핑상태: {round(client.latency * 1000,2)}ms\n읽기 속도: {round(reading_ping * 1000,2)}ms\n출력 속도: {round(response_ping * 1000,2)}ms", color=0xffd619)
        await msg.edit(embed=embed)
        return
    if message.content == prefix + '시스템':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="[시스템 정보]", color=0xffd619)
        data1 = str(psutil.cpu_percent(interval=None, percpu=False))
        data2 = str(psutil.virtual_memory().percent)
        data3 = str(psutil.disk_usage('/').percent)
        data4 = platform.system() + str(platform.release())
        if platform.system() == "Linux":
            data7 = str(round(float(str(psutil.sensors_temperatures()).split('current=')[1].split(',')[0]),2))
            embed.add_field(name="CPU:", value=data1 + "% (온도:" + data7 + "℃)", inline=True)
        else:
            embed.add_field(name="CPU:", value=data1 + "%", inline=True)
        data8 = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        total_RAM,total_type_RAM = change_data(psutil.virtual_memory()[0])
        used_RAM,used_type_RAM = change_data(psutil.virtual_memory()[3])
        total_SSD,total_type_SSD = change_data(psutil.disk_usage('/')[0])
        used_SSD,used_type_SSD = change_data(psutil.disk_usage('/')[1])
        embed.add_field(name="부팅시간:", value=data8, inline=True)
        embed.add_field(name="메모리:", value=data2 + "%(" + str(used_RAM) + str(used_type_RAM) + '/' + str(total_RAM) + str(total_type_RAM) + ')', inline=False)
        embed.add_field(name="저장공간:", value=data3 +"%(" + str(used_SSD) + str(used_type_SSD) + '/' + str(total_SSD) + str(total_type_SSD) + ')' , inline=False)
        embed.add_field(name="소프트웨어:", value=data4, inline=False)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(prefix + '블랙리스트 추가') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            mention_id = list_message[2]
        except Exception:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        cache_data = mention_id.replace("<@","",).replace(">","").replace("!","")
        if is_manager(cache_data):
            embed = discord.Embed(title="에러!",description="관리자는 블랙리스트에 추가할수 없습니다!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect .cursor()
        sql_Black = "insert into BLACKLIST(ID) value(%s)"
        cur.execute(sql_Black,cache_data)
        connect.commit()
        connect.close()
        embed = discord.Embed(title="Blacklist!",description=mention_id + "가 블랙리스트에 추가되었습니다!", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(prefix + '블랙리스트 여부'):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            tester_id = list_message[2].replace("<@","",).replace(">","").replace("!","")
        except Exception:
            tester_id = author_id
        embed = discord.Embed(title="Blacklist!",description="해당 유저가 밴당했는지 확인하는 중입니다.", color=0xaa0000)
        msg = await message.channel.send(embed=embed)
        cache = is_banned(tester_id,message)
        if cache:
            embed = discord.Embed(title="Blacklist!",description="이 사람은 블랙리스트에 등재되어 있습니다.", color=0xaa0000)
        else:
            embed = discord.Embed(title="Blacklist!",description="이 사람은 블랙리스트에 등재되어 있지 않습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        await msg.delete()
    if message.content.startswith(prefix + '블랙리스트 제거') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            mention_id = list_message[2]
        except Exception:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        cache_data1 = mention_id.replace("<@","",).replace(">","").replace("!","")
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect .cursor()
        sql_delete = "delete from BLACKLIST where ID=%s"
        try:
            cur.execute(sql_delete,cache_data1)
        except Exception:
            embed = discord.Embed(title="Blacklist!",description=mention_id + "는, 블랙리스트에 추가되어 있지 않습니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            connect.commit()
            connect.close()
            return
        connect.commit()
        connect.close()
        embed = discord.Embed(title="Blacklist!",description=mention_id + "가 블랙리스트에서 제거되었습니다!", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    if message.content == prefix + '에란겔':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Erangel_Remastered_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Erangel"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Erangel"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Erangel"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Erangel_Remastered_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '미라마':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Miramar_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Miramar"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Miramar"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Miramar"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Miramar_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '사녹':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Sanhok_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Sanhok"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Sanhok"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Sanhok"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Sanhok_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '비켄디':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Vikendi_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Vikendi"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Vikendi"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Vikendi"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Vikendi_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '카라킨':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Karakin_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Karakin"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Karakin"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Karakin"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Karakin_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '파라모':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Paramo_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Paramo"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Paramo"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Paramo"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Paramo_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content == prefix + '캠프자칼' or message.content == '훈련장':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="지도", color=0xffd619)
        map_picture = discord.File(directory + type_software + "assets" + type_software + "Maps" + type_software + "Camp_Jackal_Main_Low_Res.png")
        embed.add_field(name="원본(텍스트 삭제)",value="[링크](" + map_link["Camp_Jackal"]["No_Text_Low_Res"] + ")",inline=True)
        embed.add_field(name="고화질",value="[링크](" + map_link["Camp_Jackal"]["High_Res"] + ")",inline=True)
        embed.add_field(name="고화질(텍스트 삭제)",value="[링크](" + map_link["Camp_Jackal"]["No_Text_High_Res"] + ")",inline=True)
        embed.set_image(url="attachment://Camp_Jackal_Main_Low_Res.png")
        await message.channel.send(file=map_picture,embed=embed)
        return
    if message.content.startswith(f'{prefix}정보'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        total = 0
        for i in client.guilds:
            total += len(i.members)
        embed = discord.Embed(title='PUBG_BOT', color=0xffd619)
        embed.add_field(name='개발팀',value='[Team Developer Space](https://github.com/Team-Developer-Space)',inline=True)
        embed.add_field(name='운영팀',value='[Team Alpha | Γεαϻ Αιρηα | α](http://www.yonghyeon.com/PUBG_BOT/forum.html)',inline=True)
        embed.add_field(name='제작자',value='건유1019#0001',inline=True)
        embed.add_field(name='<:user:735138021850087476>서버수/유저수',value=f'{len(client.guilds)}서버/{total}명',inline=True)
        embed.add_field(name='PUBG BOT 버전',value=f'{version}',inline=True)
        embed.add_field(name='<:discord:735135879990870086>discord.py',value=f'v{discord.__version__}',inline=True)
        embed.set_thumbnail(url=client.user.avatar_url)
        await message.channel.send(embed=embed)
        return

@client.event
async def on_resumed():
    log_system('재시작 되었습니다.')

@client.event
async def on_guild_join(guild):
    server_number = None
    for i in client.guilds:
        if i.name == guild.name:
            server_number = client.guilds.index(i)+1
    if not server_number == None:
        log_system(guild.name + '에 가입이 확인되었습니다. 서버번호: ' + str(server_number) + '번, 서버멤버' + str(len(guild.members)) + '명')
    return

@client.event
async def on_guild_remove(guild):
    log_system(guild.name + '로 부터 추방 혹은 차단되었습니다.')
    return

@client.event
async def on_error(event, *args, **kwargs):
    if event == "on_message":
        message = args[0]
        exc = sys.exc_info()
        excname = exc[0].__name__
        excarglist = [str(x) for x in exc[1].args]
        if not excarglist:
            traceback = excname
        else:
            traceback = excname + ": " + ", ".join(excarglist)
        log_error(f"[{message.guild.name},{message.channel.name},{message.author},{message.content}]{traceback}")
        embed = discord.Embed(title="\U000026A0 에러", color=0xaa0000)
        embed.add_field(name='에러 내용(traceback)',value=f'{traceback}',inline=False)
        embed.add_field(name='서버명',value=f'{message.guild.name}',inline=True)
        embed.add_field(name='채널명',value=f'{message.channel.name}',inline=True)
        embed.add_field(name='유저명',value=f'{message.author}',inline=True)
        embed.add_field(name='메세지',value=f'{message.content}',inline=False)
        await client.get_guild(738294838063136808).get_channel(738526796575670333).send(embed=embed)
    raise

client.loop.create_task(autopost1())
client.loop.create_task(autopost2(30))
client.loop.create_task(autopost3())
client.run(token)
