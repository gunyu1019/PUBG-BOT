import discord
import asyncio
import aiohttp

import pymysql
import os
import sys
import json
import datetime
import requests_async as requests

from pytz import timezone

image_name = ["steam.png","kakao.png","xbox.png","playstation.png","stadia.png"]
platform_site = ["steam","kakao","xbox","psn","stadia"]

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

def image(pubg_platform):
    kakao = discord.File(directory + "/assets/Icon/kakao.png")
    steam = discord.File(directory + "/assets/Icon/steam.png")
    xbox = discord.File(directory + "/assets/Icon/xbox.png")
    playstation = discord.File(directory + "/assets/Icon/playstation.png")
    stadia = discord.File(directory + "/assets/Icon/stadia.png")
    image = [steam,kakao,xbox,playstation,stadia]
    return image[pubg_platform]

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

def player(html,t,user_name):
    if type(html) == dict:
        json_data = html
    else:
        json_data = json.loads(html)
    included = json_data["included"]
    for i in included:
        if i['type'] == "participant":
            if i['attributes']['stats']['playerId'] == user_name and t == 'player_id':
                return i
            elif i['id'] == user_name and t == 'id':
                return i

async def get(message,client,pubg_json,player_id,count,pubg_platform):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=f"{await player_module.name()}님의 매치히스토리(#{count+1})")
    try:
        match_id = pubg_json["data"][0]["relationships"]["matches"]["data"][count]["id"]
    except:
        embed = discord.Embed(title="에러",description="매치 조회에 실패하였습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/matches/" + match_id
    response = await requests.get(url,headers=header)
    if response.status_code == 200:
        html = response.json()
    else:
        await response_num(response,message)
        return
    map_cache = html["data"]["attributes"]["mapName"]

    user = player(html, 'player_id', player_id)
    match_user_id = user['id']
    included = html["included"]
    kill = user["attributes"]["stats"]['kills']
    assist = user["attributes"]["stats"]['assists']
    distance = round((user["attributes"]["stats"]["walkDistance"]+user["attributes"]["stats"]["swimDistance"]+user["attributes"]["stats"]["rideDistance"])/1000,3)
    deathType = user["attributes"]["stats"]["deathType"]
    deals = user["attributes"]["stats"]["damageDealt"]
    timeSurvived = user["attributes"]["stats"]["timeSurvived"]
    playtime = datetime.datetime.fromtimestamp(float(timeSurvived),timezone('UTC'))
    r_playtime = time_num(playtime)

    deathT = ["alive", "byplayer", "byzone", "suicide", "logout"]
    deathA = ["승리","유저","블루존","자살","로그 아웃"]
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

    for i in included:
        if i['type'] == "roster":
            for j in i['relationships']['participants']['data']:
                if j['id'] == match_user_id:
                    team = i
    rank = team['attributes']['stats']['rank']
    team_list = team["relationships"]["participants"]["data"]
    people = []
    for i in team_list:
        people.append(player(html, 'id', i['id'])['attributes']['stats']['name'])
    embed.add_field(name="팀원:",value=",".join(people),inline=False)
    embed.add_field(name="결과:",value=f'{deathType}({rank}위)',inline=True)
    embed.add_field(name="맵:",value=map_name[map_cache],inline=True)
    embed.add_field(name="킬/어시:",value=f"{kill}회/{assist}회",inline=True)
    embed.add_field(name="생존시간:",value=f"{r_playtime}",inline=True)
    embed.add_field(name="이동한 거리:",value=f"{distance} km",inline=True)
    embed.add_field(name="딜량:",value=f"{round(deals,2)}",inline=True)
    await message.channel.send(file=image(pubg_platform),embed=embed)
