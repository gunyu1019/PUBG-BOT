import discord

import pymysql
import os
import sys
import json
import datetime

import requests_async as requests

platform_site = ["steam","kakao","xbox","psn","stadia"]

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

connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8') #클라이언트 API키 불러오기.
cur = connect.cursor()
cur.execute("SELECT * from PUBG_BOT")
client_list = cur.fetchall()
pubg_token = client_list[0][2]
connect.close()

header = {
  "Authorization": "Bearer " + pubg_token,
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

async def season_status(player_id,season,message,pubg_platform):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    player_module = p_info.player(player_id)
    try:
        sql = "select html from NORMAL_STATUS where id=%s and season=%s"
        cur.execute(sql,(str(player_id),str(season)))
        cache = cur.fetchall()
        return_value = json.loads(cache[0][0])
        if await player_module.autopost("normal"):
            url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season)
            response = await requests.get(url,headers=header)
            if response.status_code == 200:
                return_value = response.json()
            else:
                response_num(response,message)
                return "Failed_Response"
            sql = "UPDATE NORMAL_STATUS SET html=%s WHERE id=%s"
            cur.execute(sql, (json.dumps(return_value),player_id))
            connect.commit()
            await player_module.lastupdate_insert("normal",datetime.datetime.now())
    except Exception:
        url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season)
        response = await requests.get(url,headers=header)
        if response.status_code == 200:
            return_value = response.json()
        else:
            response_num(response,message)
            return "Failed_Response"
        sql = """insert into NORMAL_STATUS(id,html,season)
                values (%s, %s, %s)"""
        cur.execute(sql, (player_id,json.dumps(return_value),season))
        connect.commit()
        await player_module.lastupdate_insert("normal",datetime.datetime.now())
    finally:
        connect.close()
    return return_value

async def season_status_update(player_id,season,message,pubg_platform):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    player_module = p_info.player(player_id)
    try:
        url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season)
        response = await requests.get(url,headers=header)
        if response.status_code == 200:
            return_value = response.json()
        else:
            response_num(response,message)
            return "Failed_Response"
        sql = "UPDATE NORMAL_STATUS SET html=%s WHERE id=%s"
        cur.execute(sql, (json.dumps(return_value),player_id))
        connect.commit()
        await player_module.lastupdate_insert("normal",datetime.datetime.now())
        connect.close()
    except Exception:
        return_value = "Failed_Response"
        connect.close()
    return return_value


async def ranked_status(player_id,season,message,pubg_platform):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    player_module = p_info.player(player_id)
    try:
        sql = "select html from RANKED_STATUS where id=%s and season=%s"
        cur.execute(sql,(str(player_id),str(season)))
        cache = cur.fetchall()
        return_value = json.loads(cache[0][0])
        if await player_module.autopost("ranked"):
            url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season) + "/ranked"
            response = await requests.get(url,headers=header)
            if response.status_code == 200:
                return_value = response.json()
            else:
                response_num(response,message)
                return "Failed_Response"
            sql = "UPDATE RANKED_STATUS SET html=%s WHERE id=%s"
            cur.execute(sql, (json.dumps(return_value),player_id))
            connect.commit()
            await player_module.lastupdate_insert("ranked",datetime.datetime.now())
    except Exception:
        url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season) + "/ranked"
        response = await requests.get(url,headers=header)
        if response.status_code == 200:
            return_value = response.json()
        else:
            response_num(response,message)
            return "Failed_Response"
        sql = """insert into RANKED_STATUS(id,html,season)
                values (%s, %s, %s)"""
        cur.execute(sql, (player_id,json.dumps(return_value),season))
        connect.commit()
        await player_module.lastupdate_insert("ranked",datetime.datetime.now())
    finally:
        connect.close()
    return return_value

async def ranked_status_update(player_id,season,message,pubg_platform):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    player_module = p_info.player(player_id)
    try:
        url = "https://api.pubg.com/shards/" + platform_site[pubg_platform] + "/players/" + str(player_id) + "/seasons/" + str(season) + "/ranked"
        response = await requests.get(url,headers=header)
        if response.status_code == 200:
            return_value = response.json()
        else:
            response_num(response,message)
            return "Failed_Response"
        sql = "UPDATE RANKED_STATUS SET id=%s WHERE html=%s"
        cur.execute(sql, (json.dumps(return_value),player_id))
        connect.commit()
        await player_module.lastupdate_insert("ranked",datetime.datetime.now())
        connect.close()
    except Exception:
        return_value = "Failed_Response"
        connect.close()
    return return_value