import discord
import asyncio
import aiohttp

import pymysql
import os
import sys
import json
import datetime

from pytz import timezone

def time_num(playtime): #시간 계산, 불필요한 월단위, 일단위 등의 제거
    if playtime.month == 1:
        if playtime.day == 1:
            if playtime.hour == 0:
                if  playtime.minute == 0:
                    return str(playtime.second)  + "초"
                return str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
            return str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
        return str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
    return str(playtime.month-1)  + "일 " + str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)

directory = os.path.dirname(os.path.abspath(__file__)).replace('\\','/').replace('/modules','')
db_f = open(directory + "/data/bot_info.json",mode='r')
db = db_f.read()
db_f.close()
db_json = json.loads(db)

db_ip = db_json["mysql"]["ip"]
db_user = db_json["mysql"]["user"]
db_pw = db_json["mysql"]["password"]
db_name = db_json["mysql"]["database"]

sys.path.append(directory + "/modules") #다른 파일내 함수추가
import player as p_info
import status as s_info

header = {
  "Accept": "application/vnd.api+json"
}

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

async def get(message,client,pubg_json,player_id,count,pubg_platform):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    match_id = json_players["data"]["relationships"]["matches"]["data"][count]["id"]
    url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/matches/" + match_id
    response = await requests.get(url,headers=header)
    if response.status_code == 200:
        json_data = response.json()
    else:
        await response_num(response,message)
    def player(html,return_value,find_value):
        if type(html) == dict:
            json_data = html
        else:
            json_data = json.loads(html)
        included = json_data["included"]
        for i in range(len(included)-1):
            if included[i]["type"] == "participant":
                if find_value == "id" and included[i]["id"] == return_value:
                    return included[i]
                elif find_value == "id":
                    continue
                elif included[i]["attributes"]["stats"][find_value] == return_value:
                    return included[i]
    map_cache = json_data["data"]["attributes"]["mapName"]
    included1 = player(json_data,player_id,"playerId")
    user_id = included1["id"]
    timeSurvived = included1["attributes"]["stats"]["timeSurvived"]
    deals = included1["attributes"]["stats"]["damageDealt"]
    kills = included1["attributes"]["stats"]["kills"]
    assists = included1["attributes"]["stats"]["assists"]
    DBNOs = included1["attributes"]["stats"]["DBNOs"]
    distance = round((included1["attributes"]["stats"]["walkDistance"]+included1["attributes"]["stats"]["swimDistance"]+included1["attributes"]["stats"]["rideDistance"])/1000,3)
    deathType = included1["attributes"]["stats"]["deathType"]
    playtime = datetime.datetime.fromtimestamp(float(timeSurvived),timezone('UTC'))
    r_playtime = time_num(playtime)
    deathT = ["alive", "byplayer", "byzone", "suicide", "logout"]
    deathA = ["생존","유저","블루존","자살","로그 아웃"]
    map_name={
        "Desert_Main": "미라마",
        "DihorOtok_Main": "비켄디",
        "Erangel_Main": "에란겔",
        "Baltic_Main": "에란겔 (리마스터)",
        "Range_Main": "캠프 자칼",
        "Savage_Main": "사녹",
        "Summerland_Main": "카라킨"
    }
    for i in range(5):
        if deathType == deathT[i]:
            deathType = deathA[i]
            break
    included = json_data["included"]
    for i in range(len(included)-1):
        if included[i]["type"] == "roster":
            party = included[i]["relationships"]["participants"]["data"]
            a_tf = False
            for j in range(len(party)):
                if party[j]["id"] == user_id:
                    a_tf = True
                    break
            if a_tf:
                rank = included[i]["attributes"]["stats"]["rank"]
                break
    if not a_tf:
        team_member = "멤버를 불러오지 못했습니다."
    team_member = ""
    for i in range(len(party)):
        player_m = player(json_data,party[i]["id"],"id")
        team_member = team_member + "," + str(player_m["attributes"]["stats"]["name"])
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    embed.add_field(name="팀원:",value=team_member.replace(',','',1),inline=False)
    embed.add_field(name="맵:",value=map_name[map_cache],inline=True)
    embed.add_field(name="킬/어시:",value=str(kills) + "회/" + str(assists) + "회",inline=True)
    embed.add_field(name="DBNOs:",value=str(DBNOs) + "회",inline=True)
    embed.add_field(name="결과:",value=deathType + "(" + str(rank) + "위)",inline=True)
    embed.add_field(name="이동한 거리:",value=str(distance) + "km",inline=True)
    embed.add_field(name="딜량:",value=str(round(deals,2)),inline=True)
    if update:
        await update_msg.delete()
    msg2 = await message.channel.send(embed=embed)