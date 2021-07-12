import discord

import pymysql
import os
import sys
import json
import datetime

from pytz import timezone

image_name = ["steam.png","kakao.png","xbox.png","playstation.png","stadia.png"]
platform_name = ["Steam","Kakao","XBOX","PS","Stadia"]

#동기적으로 처리할수 있는 전적검색 유형의 함수
def ranking(rank,lng): #랭킹별 티어 분석
    if rank == "0":
        if lng == 0:
            return "무티어","assets/Ranks/unranked.png"
        return "Unranked"
    title = int(rank[0])
    if len(rank.replace('-','')) == 2:
        level = int(rank.replace('-','')[1])
    else:
        level = 0
    level_l = [""," I"," II"," III"," IV","V"]
    picture_l = ["unranked","bronze","silver","gold","platinum","diamond","elite","master","grandmaster"]
    if lng == 0:
        title_ko = ["초심","견습","경험","숙련","전문","달인","생존자","유일한 생존자"]
        return title_ko[title] + level_l[level],"assets/Ranks/" + picture_l[title] + ".png"
    elif lng == 1:
        title_en = ["Beginner","Novice","Experienced","Skilled","Specialist","Expert","Survivor","Lone Survivor"]
        return title_en[title] + level_l[level], "assets/Ranks/" + picture_l[title] + ".png"
    return "Not Found","assets/Ranks/" + picture_l[0] + ".png"

def image(pubg_platform):
    kakao = discord.File(directory + "/assets/Icon/kakao.png")
    steam = discord.File(directory + "/assets/Icon/steam.png")
    xbox = discord.File(directory + "/assets/Icon/xbox.png")
    playstation = discord.File(directory + "/assets/Icon/playstation.png")
    stadia = discord.File(directory + "/assets/Icon/stadia.png")
    image = [steam,kakao,xbox,playstation,stadia]
    return image[pubg_platform]

def time_num(playtime): #시간 계산, 불필요한 월단위, 일단위 등의 제거
    if playtime.month == 1:
        if playtime.day == 1:
            if playtime.hour == 0:
                if  playtime.minute == 0:
                    return str(playtime.second)  + "초"
                return str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
            return str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
        return str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
    return str(playtime.month-1)  + "달 " + str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)

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

async def profile_total(message,client,pubg_platform,pubg_type,pubg_json,season,player_id):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=await player_module.name() + "님의 전적")
    if pubg_type == "tpp":
        game_mode = ["solo","duo","squad"]
        list_name = ["솔로(Solo)","듀오(Duo)","스쿼드(Squad)"]
    else:
        game_mode = ["solo-fpp","duo-fpp","squad-fpp"]
        list_name = ["솔로 1인칭(Solo)","듀오 1인칭(Duo)","스쿼드 1인칭(Squad)"]
    count = 3
    for i in range(count):
        json_c = pubg_json["data"]["attributes"]["gameModeStats"][game_mode[i]]
        win = str(json_c["wins"])
        top10 = str(json_c["top10s"])
        lose = str(json_c["losses"])
        kills = str(json_c["kills"])
        f_playtime = float(json_c["timeSurvived"])
        playtime = datetime.datetime.fromtimestamp(f_playtime,timezone('UTC'))
        a_playtime = time_num(playtime)
        if int(lose) != 0:
            KD = str(round(int(kills) / int(lose),2))
        else:
            KD = str(round(int(kills) / 1,2))
        embed.add_field(name=list_name[i] + ":",value=win + "승 " + top10 + "탑 " + lose + "패\n" + a_playtime + "\n킬: " + kills + "회(" + KD + "점)",inline=True)
    last_update = await player_module.lastupdate("normal")
    embed.set_footer(text="최근 업데이트: " + last_update.strftime('%Y년 %m월 %d일 %p %I:%M'))
    msg1 = await message.channel.send(file=image(pubg_platform),embed=embed)
    for i in range(5):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 솔로전적 \U00000032\U0000FE0F\U000020E3 : 듀오 전적 \U00000033\U0000FE0F\U000020E3 : 스쿼드 전적 \U00000034\U0000FE0F\U000020E3 : 전적 업데이트\U00000035\U0000FE0F\U000020E3 : 메뉴 종료")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(5):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,_ = await client.wait_for('reaction_add', check=check)
    if pubg_type == "fpp":
        add_type = "-fpp"
    else:
        add_type = ""
    if reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_mode(message,client,pubg_platform,"fpp","solo" + add_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_mode(message,client,pubg_platform,"fpp","duo" + add_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_mode(message,client,pubg_platform,"fpp","squad" + add_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000034\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        update_json = await s_info.season_status_update(player_id,season,message,pubg_platform)
        if update_json == "Failed_Response":
            return
        await profile_total(message,client,pubg_platform,pubg_type,update_json,season,player_id)
    elif reaction.emoji == "\U00000035\U0000FE0F\U000020E3":
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed_waring = discord.Embed(title="\U000026A0경고!",description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.", color=0xffd619)
            await message.channel.send(embed=embed_waring)
        await msg2.delete()
    return

async def profile_mode_status(message,client,pubg_platform,pubg_type,mode,pubg_json,season,player_id):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=await player_module.name() + "님의 전적")
    json_c = pubg_json["data"]["attributes"]["gameModeStats"][mode]
    assists = json_c["assists"]
    boosts = json_c["boosts"]
    dBNOs = json_c["dBNOs"]
    dailyKills = json_c["dailyKills"]
    dailyWins = json_c["dailyWins"]
    damageDealt = json_c["damageDealt"]
    days = json_c["days"]
    headshotKills = json_c["headshotKills"]
    heals = json_c["heals"]
    kills = json_c["kills"]
    longestKill = json_c["longestKill"]
    longestTimeSurvived = json_c["longestTimeSurvived"]
    losses = json_c["losses"]
    maxKillStreaks = json_c["maxKillStreaks"]
    mostSurvivalTime = json_c["mostSurvivalTime"]
    revives = json_c["revives"]
    rideDistance = json_c["rideDistance"]
    roadKills = json_c["roadKills"]
    #roundMostKills = json_c["roundMostKills"]
    #roundsPlayed = json_c["roundsPlayed"]
    suicides = json_c["suicides"]
    swimDistance = json_c["swimDistance"]
    teamKills = json_c["teamKills"]
    timeSurvived = json_c["timeSurvived"]
    top10s = json_c["top10s"]
    vehicleDestroys = json_c["vehicleDestroys"]
    walkDistance = json_c["walkDistance"]
    weaponsAcquired = json_c["weaponsAcquired"]
    weeklyKills = json_c["weeklyKills"]
    weeklyWins = json_c["weeklyWins"]
    wins = json_c["wins"]
    season_count = season.replace("division.bro.official.pc-2018","")
    if int(season_count) < 7:
        _, rank_icon = ranking(json_c["rankPointsTitle"],0)
        embed.set_thumbnail(url="attachment://" + rank_icon.replace("assets/Ranks/",""))
        icon = discord.File(directory + "/" + rank_icon)
    if int(wins) + int(top10s) + int(losses) == 0:
        winper = "0"
    else:
        winper = str(int(wins) / (int(wins) + int(top10s) + int(losses)) * 100)
    if int(kills) != 0:
        headshot_per = str(int(headshotKills) / int(kills) * 100)
    else:
        headshot_per = "0"
    if int(losses) != 0:
        KD = str(round(int(kills) / int(losses),2))
    else:
        KD = str(round(int(kills) / 1,2))
    playtime1 = datetime.datetime.fromtimestamp(float(timeSurvived),timezone('UTC'))
    playtime2 = datetime.datetime.fromtimestamp(float(longestTimeSurvived),timezone('UTC'))
    playtime3 = datetime.datetime.fromtimestamp(float(mostSurvivalTime),timezone('UTC'))
    a_playtime = time_num(playtime1)
    max_playtime = time_num(playtime2)
    average_playtime = time_num(playtime3)
    def distance(distance):
        return str(round(float(distance)/1000,2))
    data1 = "게임 수:" + str(int(wins) + int(top10s) + int(losses)) + "회\n승리:" + str(wins) + "회\nTop10:" + str(top10s) + "회\n패배:" + str(losses) + "회\n승률:" + winper + "%\n일간 승리:" + str(dailyWins) + "회\n주간 승리:" + str(weeklyWins) + "회"
    data2 = "일간 킬 수" + str(dailyKills) + "회\n주간 킬 수:" + str(weeklyKills) + "회\n게임당 최다 킬 수:" +  str(maxKillStreaks) + "회\n누적 킬 수:" +  str(kills) + "회\n헤드샷:" +  str(headshotKills) + "회(" + headshot_per + "%)\n어시스트:" +  str(assists) + "회\nK/D:" +  KD + "\n차량 파괴:" +  str(vehicleDestroys) + "회\n로드킬:" +  str(roadKills) + "회\n최장 킬 거리:" +  str(round(float(longestKill),2)) + "m\n자살:" +  str(suicides) + "회\n팀킬:" +  str(teamKills) + "회"
    data3 = "플레이 시간:" + a_playtime + "\n이번 시즌 게임 접속일:" + str(days) + "일\n최대 생존 시간:" + max_playtime + "\n평균 생존 시간:" + average_playtime + "\n치유:" + str(heals) + "회\n부스트:" + str(boosts) + "회"
    data4 = "종합 이동 거리:" + str(round(float(distance(walkDistance)) + float(distance(rideDistance)) + float(distance(swimDistance)),2)) + "km\n걸어간 거리:" + distance(walkDistance) + "km\n탑승 거리:" + distance(rideDistance) + "km\n평균 생존 시간:" + distance(swimDistance) + "km"
    data5 = "누적 입힌 피해:" + str(round(float(damageDealt),2)) + "\n무기 획득 횟수:" + str(weaponsAcquired) + "회\nDBNO:" + str(dBNOs) + "회\n소생:" + str(revives) + "회"
    embed.add_field(name="플레이 기록:",value=data1,inline=False)
    embed.add_field(name="전투 기록:",value=data2,inline=False)
    embed.add_field(name="게임 플레이:",value=data3,inline=False)
    embed.add_field(name="이동 거리:",value=data4,inline=False)
    embed.add_field(name="기타:",value=data5,inline=False)
    last_update = await player_module.lastupdate("normal")
    embed.set_footer(text="최근 업데이트: " + last_update.strftime('%Y년 %m월 %d일 %p %I:%M'))
    if int(season_count) < 7:
        icons = [image(pubg_platform),icon]
        msg1 = await message.channel.send(files=icons,embed=embed)
    else:
        msg1 = await message.channel.send(file=image(pubg_platform),embed=embed)
    for i in range(3):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 개요 \U00000032\U0000FE0F\U000020E3 : 전적 정보 업데이트 \U00000033\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(3):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,_ = await client.wait_for('reaction_add', check=check)
    if reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_mode(message,client,pubg_platform,pubg_type,mode,pubg_json,season,player_id)
        #await profile_mode(message,client,pubg_platform,pubg_type,mode,update_json,season,player_id)
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        update_json = await s_info.season_status_update(player_id,season,message,pubg_platform)
        if update_json == "Failed_Response":
            return
        await profile_mode_status(message,client,pubg_platform,pubg_type,mode,update_json,season,player_id)
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed_waring = discord.Embed(title="\U000026A0경고!",description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.", color=0xffd619)
            await message.channel.send(embed=embed_waring)
        await msg2.delete()
    return

async def profile_mode(message,client,pubg_platform,pubg_type,mode,pubg_json,season,player_id):
    icon = [image(pubg_platform),None]
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=await player_module.name() + "님의 전적")
    json_c = pubg_json["data"]["attributes"]["gameModeStats"][mode]
    win = str(json_c["wins"])
    top10 = str(json_c["top10s"])
    lose = str(json_c["losses"])
    kills = str(json_c["kills"])
    if int(lose) != 0:
        KD = str(round(int(kills) / int(lose),2))
    else:
        KD = str(round(int(kills) / 1,2))
    assists = str(json_c["assists"])
    dBNOs = str(json_c["dBNOs"])
    maxkill = str(json_c["maxKillStreaks"])
    f_playtime = float(json_c["timeSurvived"])
    playtime = datetime.datetime.fromtimestamp(f_playtime,timezone('UTC'))
    a_playtime = time_num(playtime)
    if int(kills) != 0:
        headshot = str(round(int(json_c["headshotKills"]) / int(kills) * 100,1))
    else:
        headshot = "0"
    distance = str(round(float(json_c["longestKill"]),2))
    if int(json_c["roundsPlayed"]) != 0:
        deals = str(round(float(json_c["damageDealt"])/float(json_c["roundsPlayed"]),2))
    else:
        deals = "0"
    season_count = season.replace("division.bro.official.pc-2018","")
    if int(season_count) < 7:
        _, rank_icon = ranking(json_c["rankPointsTitle"],0)
        embed.set_thumbnail(url="attachment://" + rank_icon.replace("assets/Ranks/",""))
        icon = discord.File(directory + "/" + rank_icon)
    embed.add_field(name="승/탑/패:",value=win + "승 " + top10 + "탑 " + lose + "패",inline=True)
    embed.add_field(name="플레이타임:",value=a_playtime,inline=True)
    embed.add_field(name="킬(K/D):",value=kills + "회(" + KD + "점)",inline=True)
    embed.add_field(name="어시:",value=assists + "회",inline=True)
    embed.add_field(name="dBNOs:",value=dBNOs + "회",inline=True)
    embed.add_field(name="여포:",value=maxkill + "회",inline=True)
    embed.add_field(name="헤드샷:",value=headshot + "%",inline=True)
    embed.add_field(name="딜량:",value=deals,inline=True)
    embed.add_field(name="거리:",value=distance + "m",inline=True)
    last_update = await player_module.lastupdate("normal")
    embed.set_footer(text="최근 업데이트: " + last_update.strftime('%Y년 %m월 %d일 %p %I:%M'))
    if int(season_count) < 7:
        icons = [image(pubg_platform),icon]
        msg1 = await message.channel.send(files=icons,embed=embed)
    else:
        msg1 = await message.channel.send(file=image(pubg_platform),embed=embed)
    for i in range(4):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 상세정보 \U00000032\U0000FE0F\U000020E3 : 전적 정보 업데이트 \U00000033\U0000FE0F\U000020E3 :  종합 전적 \U00000034\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(4):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,_ = await client.wait_for('reaction_add', check=check)
    if reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_mode_status(message,client,pubg_platform,pubg_type,mode,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        update_json = await s_info.season_status_update(player_id,season,message,pubg_platform)
        if update_json == "Failed_Response":
            return
        await profile_mode(message,client,pubg_platform,pubg_type,mode,update_json,season,player_id)
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await profile_total(message,client,pubg_platform,pubg_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000034\U0000FE0F\U000020E3":
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed_waring = discord.Embed(title="\U000026A0경고!",description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.", color=0xffd619)
            await message.channel.send(embed=embed_waring)
        await msg2.delete()
    return