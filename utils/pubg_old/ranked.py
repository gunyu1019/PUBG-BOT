import discord

import pymysql
import os
import sys
import json
import datetime

from pytz import timezone

image_name = ["steam.png","kakao.png","xbox.png","playstation.png","stadia.png"]
platform_name = ["Steam","Kakao","XBOX","PS","Stadia"]

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

async def ranked_mode(message,client,pubg_platform,pubg_type,mode,pubg_json,season,player_id):
    icon = [image(pubg_platform),None]
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=await player_module.name() + "님의 전적")
    try:
        json_c = pubg_json["data"]["attributes"]["rankedGameModeStats"][mode]
    except KeyError:
        embed.description = "기록이 없습니다."
        msg1 = await message.channel.send(embed=embed)
    else:
        currentTier1 = json_c["currentTier"]["tier"]
        currentTier2 = json_c["currentTier"]["subTier"]
        bestTier1 = json_c["bestTier"]["tier"]
        bestTier2 = json_c["bestTier"]["subTier"]
        if currentTier1 == "Unranked" or currentTier1 == "Master":
            tier_name1 = currentTier1
            rank_icon = currentTier1 + ".png"
        else:
            tier_name1 = currentTier1 + " " + str(currentTier2)
            rank_icon = currentTier1 + "-" + str(currentTier2) + ".png"
        if bestTier1 == "Unranked" or bestTier1 == "Master":
            tier_name2 = bestTier1
        else:
            tier_name2 = bestTier1 + " " + str(bestTier2)
        point1 = json_c["currentRankPoint"]
        point2 = json_c["bestRankPoint"]
        assists = json_c["assists"]
        avgRank = json_c["avgRank"]
        damageDealt = json_c["damageDealt"]
        dBNOs = json_c["dBNOs"]
        wins = json_c["wins"]
        losses = json_c["deaths"]
        total = json_c["roundsPlayed"]
        top10 = str(round((total * json_c["top10Ratio"]) - wins,0))
        kills = json_c["kills"]
        kda = json_c["kda"]
        embed.set_thumbnail(url="attachment://" + rank_icon)
        icon[1] = discord.File(directory+ "/assets/Insignias/" + rank_icon)
        embed.add_field(name="현재 점수:",value=tier_name1 + "(" + str(point1) + "점)",inline=True)
        embed.add_field(name="최고 점수:",value=tier_name2 + "(" + str(point2) + "점)",inline=True)
        embed.add_field(name="승/탑/패:",value=str(wins) + "승 " + top10 + "탑 " + str(losses) + "패",inline=True)
        embed.add_field(name="킬(K/D/A):",value=str(kills) + "회(" + str(round(kda,1)) + "점)",inline=True)
        embed.add_field(name="어시:",value=str(assists) + "회",inline=True)
        embed.add_field(name="dBNOs:",value=str(dBNOs) + "회",inline=True)
        embed.add_field(name="평균 등수:",value=str(round(avgRank,1)),inline=True)
        embed.add_field(name="딜량:",value=str(round(damageDealt,2)),inline=True)
        last_update = await player_module.lastupdate("ranked")
        embed.set_footer(text="최근 업데이트: " + last_update.strftime('%Y년 %m월 %d일 %p %I:%M'))
        msg1 = await message.channel.send(files=icon,embed=embed)
    for i in range(3):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 개요 \U00000032\U0000FE0F\U000020E3 : 전적 업데이트 \U00000033\U0000FE0F\U000020E3 : 메뉴 종료")
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
        await ranked_total(message,client,pubg_platform,pubg_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        update_json = await s_info.ranked_status_update(player_id,season,message,pubg_platform)
        if update_json == "Failed_Response":
            return
        await ranked_mode(message,client,pubg_platform,pubg_type,mode,update_json,season,player_id)
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed_waring = discord.Embed(title="\U000026A0경고!",description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.", color=0xffd619)
            await message.channel.send(embed=embed_waring)
        await msg2.delete()
    return

async def ranked_total(message,client,pubg_platform,pubg_type,pubg_json,season,player_id):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    player_module = p_info.player(player_id)
    embed.set_author(icon_url="attachment://" + image_name[pubg_platform] ,name=await player_module.name() + "님의 전적")
    if pubg_type == "tpp":
        game_mode = ["solo","squad"]
        list_name = ["솔로(Solo)","스쿼드(Squad)"]
    else:
        game_mode = ["solo-fpp","squad-fpp"]
        list_name = ["솔로 1인칭(Solo)","스쿼드 1인칭(Squad)"]
    count = 2
    for i in range(count):
        try:
            json_c = pubg_json["data"]["attributes"]["rankedGameModeStats"][game_mode[i]]
            currentTier1 = json_c["currentTier"]["tier"]
            currentTier2 = json_c["currentTier"]["subTier"]
            if currentTier1 == "Unranked" or currentTier1 == "Master":
                tier_name = currentTier1
            else:
                tier_name = currentTier1 + " " + str(currentTier2)
            #bestTier1 = json_c["bestTier"]["tier"]
            #bestTier2 = json_c["bestTier"]["subTier"]
            point = json_c["currentRankPoint"]
            #point2 = json_c["bestRankPoint"]
            wins = json_c["wins"]
            losses = json_c["deaths"]
            total = json_c["roundsPlayed"]
            top10 = str(round((total * json_c["top10Ratio"]) - wins,0))
            kills = json_c["kills"]
            kda = json_c["kda"]
            embed.add_field(name=list_name[i] + ":",value="티어: " + tier_name + "(" + str(point) + "점)"+ "\n" + str(wins) + "승" + top10 + "탑" + str(losses) + "패\n킬:" + str(kills) + "(KDA: " + str(round(kda,1)) + "점)",inline=True)
        except Exception:
            embed.add_field(name=list_name[i] + ":",value="기록 없음",inline=True)
    last_update = await player_module.lastupdate("ranked")
    embed.set_footer(text="최근 업데이트: " + last_update.strftime('%Y년 %m월 %d일 %p %I:%M'))
    msg1 = await message.channel.send(file=image(pubg_platform),embed=embed)
    for i in range(4):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 솔로(경쟁전) 전적 \U00000032\U0000FE0F\U000020E3 : 스쿼드(경쟁전) 전적 \U00000033\U0000FE0F\U000020E3 : 전적 업데이트\U00000034\U0000FE0F\U000020E3 : 메뉴 종료")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(4):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id 
    reaction, _ = await client.wait_for('reaction_add', check=check)
    if pubg_type == "fpp":
        add_type = "-fpp"
    else:
        add_type = ""
    if reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await ranked_mode(message,client,pubg_platform,pubg_type,"solo" + add_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        await ranked_mode(message,client,pubg_platform,pubg_type,"squad" + add_type,pubg_json,season,player_id)
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.delete()
        await msg2.delete()
        update_json = await s_info.ranked_status_update(player_id,season,message,pubg_platform)
        if update_json == "Failed_Response":
            return
        await ranked_total(message,client,pubg_platform,pubg_type,update_json,season,player_id)
    elif reaction.emoji == "\U00000034\U0000FE0F\U000020E3":
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed_waring = discord.Embed(title="\U000026A0경고!",description="권한설정이 잘못되었습니다! 메세지 관리를 활성해 주세요.\n메세지 관리 권한이 활성화 되지 않을 경우 디스코드봇이 정상적으로 작동하지 않습니다.", color=0xffd619)
            await message.channel.send(embed=embed_waring)
        await msg2.delete()
    return
