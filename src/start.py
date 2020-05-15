import discord
import asyncio
import os
import datetime
import platform
import pymysql
import io
import csv
import requests_async as requests
import json

from matplotlib import pyplot as plt
from pytz import timezone

connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8') #클라이언트 API키 불러오기.
cur = connect .cursor()
cur.execute("SELECT * from PUBG_BOT")
client_list = cur.fetchall()
token = client_list[0][0]
pubg_token = client_list[0][2]
connect.close()

client = discord.Client()
header = {
  "Authorization": "Bearer " + pubg_token,
  "Accept": "application/vnd.api+json"
}
directory = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Windows":
    type_software = '\\'
elif platform.system() == "Linux":
    type_software = '/'
i_date = "starting"
DB_players = [0,0,0,0,0,0,0,0,0,0,0,0]
DB_datetime = [i_date,i_date,i_date,i_date,i_date,i_date,i_date,i_date,i_date,i_date,i_date,i_date]

def is_manager(user_id):
    if platform.system() == "Windows":
        file = open(directory + "\\USER_setting\\Manager.txt",mode='r')
    elif platform.system() == "Linux":
        file = open(directory + "/USER_setting/Manager.txt",mode='r')
    else:
        return False
    cache1 = file.readlines()
    file.close()
    for i in range(len(cache1)):
        if user_id == cache1[i]:
            return True
    return False

def is_admin(message):
    for i in range(len(message.author.roles)):
        cache2 = message.author.roles[i].permissions.administrator
        if cache2:
            return True
            break
    return False    

def log_info(message):
    connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8')
    cur = connect .cursor()
    rtime = time.strftime('%Y-%m-%d %p %I:%M:%S', time.localtime(time.time()))
    sql = "insert into customer(datetime,guild,channel,author,message) values (%s, %s, %s, %s, %s)"
    print("[시간: " + str(rtime) + " | " + str(message.guild) + " | " + str(message.channel) + " | " + str(message.author) + "]: " + str(message.connect))
    curs.execute(sql, (rtime,message.guild,message.channel,message.author,message.connect))
    connect.commit()
    connect.close()
    return

def is_banned(user_id,message):
    connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8')
    cur = connect .cursor()
    sql_prefix = "select * from BLACKLIST"
    cur.execute(sql_prefix)
    banned_list = cur.fetchall()
    connect.close()
    for i in range(len(banned_list)):
        print(banned_list[i][0])
        if banned_list[i][0] == int(user_id):
            if message.content[1:].startswith("블랙리스트 여부"):
                log_info(message.guild,message.channel,'Blacklist-BOT',str(message.author) + '잘못된 유저가 접근하고 있습니다!(' + message.content + ')')
                embed = discord.Embed(title="권한 거부(403)", color=0x00aaaa)
                embed.add_field(name="권한이 거부되었습니다.", value="당신은 블랙리스트로 등록되어 있습니다.", inline=False)
                coro = message.channel.send(embed=embed)
                asyncio.run_coroutine_threadsafe(coro, client.loop)
            return True
    return False

async def player(nickname,message):
    response2 = await requests.get("https://api.pubg.com/shards/steam/players?filter[playerNames]=" + nickname, headers=header)
    if response2.status_code == 200:
        html_c = response2.text
    else:
        await response_num(response2, message, None, False)
        return "False"
    return html_c.split('"id":')[1].split(',')[0].replace('"', '').replace(' ', '')

async def top_season(message):
    response1 = await requests.get("https://api.pubg.com/shards/steam/seasons",headers=header)
    if response1.status_code == 200:
        html_s = response1.text
    else:
        await response_num(response1,message,None,False)
        return "False"
    season_id_list = html_s.split('"id":"')
    return season_id_list[len(season_id_list)-1].split('"')[0].replace(' ','')

def ranking(rank,lng): #랭킹별 티어 분석
    if rank == "0":
        if lng == 0:
            return "무티어","Assets" + type_software + "Rank" + type_software + "unranked.png"
        else:
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
        return title_ko[title] + level_l[level],"Assets" + type_software + "Rank" + type_software + picture_l[title] + ".png"
    elif lng == 1:
        title_en = ["Beginner","Novice","Experienced","Skilled","Specialist","Expert","Survivor","Lone Survivor"]
        return title_en[title] + level_l[level], "Assets" + type_software + "Rank" + type_software + picture_l[title] + ".png"
    else:
        return "Not Found","Assets" + type_software + "Rank" + type_software + picture_l[0] + ".png"

def time_num(playtime): #시간 계산, 불필요한 월단위, 일단위 등의 제거
    if playtime.month == 1:
        if playtime.day == 1:
            if playtime.hour == 0:
                if  playtime.minute == 0:
                    return str(playtime.second)  + "초"
                else:
                    return str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
            else:
                return str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
        else:
            return str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
    else:
        return str(playtime.month-1)  + "일 " + str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"

async def autopost(time):
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

async def response_num(response,message,update_msg,update): #에러 발생시, 코드를 통하여 분석
    a_num = int(response.status_code)
    if a_num == 200:
        return
    elif a_num == 400:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="닉네임을 입력해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 401:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="DB 불러오는것을 실패하였습니다. 잠시후 다시시도 해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 404:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="해당 유저를 찾을수 없습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 415:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="콘텐츠 지정이 잘못되었습니다. 봇 제작자에게 문의해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 429:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="너무 많은 요청이 들어왔습니다. 잠시후 다시시도해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    else:
        embed = discord.Embed(title="에러",description="알수없는 에러가 발생하였습니다. 관리자에게 문의해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
    return

async def matches(message,platform,update,update_msg,match,player_id,season):
    if update == 1:
         match_id = match
    elif update == 0:
        embed = discord.Embed(title="PUBG",description="최근 검색하실 전적을 고르시기 바랍니다.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check1(reaction,user):
            for i in range(5):
                if str(i+1) + "️⃣" == reaction.emoji:
                    return user.id == message.author.id and msg1.id==reaction.message.id
        for i in range(5):
            await msg1.add_reaction(str(i+1) +  "\U0000FE0F\U000020E3")
        reaction,user = await client.wait_for('reaction_add', check=check1)
        count = 1
        for i in range(5):
            if str(i+1) + "️⃣" == reaction.emoji:
                count = i
                break
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed = discord.Embed(title="\U000026A0경고!",description="디스코드봇에게 \"메세지 관리\"권한을 부여해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
        if platform == "Kakao":
            url1 = "https://api.pubg.com/shards/kakao/players/" + player_id
        else:
            url1 = "https://api.pubg.com/shards/steam/players/" + player_id
        response1 = await requests.get(url1,headers=header)
        html1 = response1.text
        json_players = json.loads(html1)
        match_id = json_players["data"]["relationships"]["matches"]["data"][count]["id"]
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
    if platform == "Kakao":
        url2 = "https://api.pubg.com/shards/kakao/matches/" + match_id
    elif platform == "Steam":
        url2 = "https://api.pubg.com/shards/steam/matches/" + match_id
    response2 = await requests.get(url2,headers=header)
    html2 = response2.text
    json_data = json.loads(html2)
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
    if platform == "Steam":
        icon = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "steam.png")
        embed.set_author(icon_url="attachment://steam.png",name=message.content.split(" ")[1] + "님의 전적")
    elif platform == "Kakao":
        icon = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "kakao.jpg")
        embed.set_author(icon_url="attachment://kakao.jpg",name=message.content.split(" ")[1] + "님의 전적")
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
    try:
        await msg1.delete()
    except:
        pass
    for i in range(2):
        await msg2.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg3 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 종합전적 확인하기 \U00000032\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg2.id
    def check2(reaction, user):
        for i in range(2):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,user = await client.wait_for('reaction_add', check=check2)
    if reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg2.clear_reactions()
        await msg3.delete()
        return
    elif reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg2.clear_reactions()
        await msg3.delete()
        if platform == "Kakao":
            url = "https://api.pubg.com/shards/kakao/players/" + player_id + "/seasons/" + season
        else:
            url = "https://api.pubg.com/shards/steam/players/" + player_id + "/seasons/" + season
        response1 = await requests.get(url,headers=header)
        if response1.status_code == 200:
            html = response1.text
        else:
            await response_num(response1,message,msg2,True)
            return
        await profile_total(message,platform,True,msg2,html,url,player_id)
        return
    return

async def weapon(message,platform,html,url,gun,update,update_msg,player_id):
    if update == 0:
        embed = discord.Embed(title="PUBG",description="검색하실 총이름을 작성해주세요.\nex.)\"M416\" ", color=0xffd619)
        msg = await message.channel.send(embed=embed)
        def check(m):
            return m.channel.id == message.channel.id and m.author.id == message.author.id
        gun_message = await client.wait_for("message",check=check)
        gt = False
        f = open(directory + type_software + "Data" + type_software + "gun_info.csv", 'r', encoding='utf-8')
        gun_list = csv.reader(f)
        for line in gun_list:
            if str(line[0]) == gun_message.content:
                gun_name = line[0]
                gun_id = line[1]
                gun_picutre = line[2]
                gt = True
                break
        f.close()
        if not gt:
            embed = discord.Embed(title="에러",description="총을 찾지 못했습니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            return
    elif update == 2:
        list_message  = message.content.split(" ")
        try:
            gun_message = list_message[2]
        except:
            embed = discord.Embed(title="PUBG",description="검색하실 총이름을 작성해주세요.\nex.)\"M416\" ", color=0xffd619)
            msg = await message.channel.send(embed=embed)
            def check(m):
                return m.channel.id == message.channel.id and m.author.id == message.author.id
            gun_message = await client.wait_for("message",check=check)
        gt = False
        f = open(directory + type_software + "Data" + type_software + "gun_info.csv", 'r', encoding='utf-8')
        gun_list = csv.reader(f)
        for line in gun_list:
            if str(line[0]) == gun_message.content:
                gun_name = line[0]
                gun_id = line[1]
                gun_picutre = line[2]
                gt = True
                break
        f.close()
        if not gt:
            embed = discord.Embed(title="에러",description="총을 찾지 못했습니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            return
    else:
        gun_id = gun
        f = open(directory + type_software + "Data" + type_software + "gun_info.csv", 'r', encoding='utf-8')
        gun_list = csv.reader(f)
        for line in  gun_list:
            if line[1] == gun_id:
                gun_name = line[0]
                gun_picutre = line[2]
                break
        f.close()
    html_c = html.split('"' + gun_id + '":{')[1].split('}')[0].replace(" ","")
    xp = html_c.split('"XPTotal":')[1].split(',')[0].replace(" ","")
    kill = html_c.split('"Kills":')[1].split(',')[0].replace(" ","")
    head = html_c.split('"HeadShots":')[1].split(',')[0].replace(" ","")
    lose = html_c.split('"Defeats":')[1].split(',')[0].replace(" ","")
    mhead = html_c.split('"MostHeadShotsInAGame":')[1].split(',')[0].replace(" ","")
    mkill = html_c.split('"MostKillsInAGame":')[1].split(',')[0].replace(" ","")
    damage = str(round(float(html_c.split('"DamagePlayer":')[1].split(',')[0].replace(" ","")),2))
    mdamage = str(round(float(html_c.split('"MostDamagePlayerInAGame":')[1].split(',')[0].replace(" ","")),2))
    icon = discord.File(directory + type_software + "Assets" + type_software + "Weapon" + type_software + gun_picutre)
    embed.set_thumbnail(url="attachment://" + gun_picutre)
    embed.add_field(name="XP:",value=xp + "점",inline=True)
    embed.add_field(name="킬:",value=kill + "회(" + mkill + "회)",inline=True)
    embed.add_field(name="헤드샷:",value=head + "회(" + mhead + "회)",inline=True)
    embed.add_field(name="피해량:",value=damage + "(" + mdamage + ")",inline=True)
    embed.add_field(name="패베:",value=lose + "회",inline=True)
    msg1 = await message.channel.send(file=icon,embed=embed)
    
async def profile_mode_status(message,platform,html_c,url,game_mode,player_id):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    assists = html_c.split('"assists":')[1].split(',')[0]
    boosts = html_c.split('"boosts":')[1].split(',')[0]
    dBNOs = html_c.split('"dBNOs":')[1].split(',')[0]
    dailyKills = html_c.split('"dailyKills":')[1].split(',')[0]
    dailyWins = html_c.split('"dailyWins":')[1].split(',')[0]
    damageDealt = html_c.split('"damageDealt":')[1].split(',')[0]
    days = html_c.split('"days":')[1].split(',')[0]
    headshotKills = html_c.split('"headshotKills":')[1].split(',')[0]
    heals = html_c.split('"heals":')[1].split(',')[0]
    kills = html_c.split('"kills":')[1].split(',')[0]
    longestKill = html_c.split('"longestKill":')[1].split(',')[0]
    longestTimeSurvived = html_c.split('"longestTimeSurvived":')[1].split(',')[0]
    losses = html_c.split('"losses":')[1].split(',')[0]
    maxKillStreaks = html_c.split('"maxKillStreaks":')[1].split(',')[0]
    mostSurvivalTime = html_c.split('"mostSurvivalTime":')[1].split(',')[0]
    rank_point = str(round(float(html_c.split('"rankPoints":')[1].split(',')[0]),1))
    revives = html_c.split('"revives":')[1].split(',')[0]
    rideDistance = html_c.split('"rideDistance":')[1].split(',')[0]
    roadKills = html_c.split('"roadKills":')[1].split(',')[0]
    roundMostKills = html_c.split('"roundMostKills":')[1].split(',')[0]
    roundsPlayed = html_c.split('"roundsPlayed":')[1].split(',')[0]
    suicides = html_c.split('"suicides":')[1].split(',')[0]
    swimDistance = html_c.split('"swimDistance":')[1].split(',')[0]
    teamKills = html_c.split('"teamKills":')[1].split(',')[0]
    timeSurvived = html_c.split('"timeSurvived":')[1].split(',')[0]
    top10s = html_c.split('"top10s":')[1].split(',')[0]
    vehicleDestroys = html_c.split('"vehicleDestroys":')[1].split(',')[0]
    walkDistance = html_c.split('"walkDistance":')[1].split(',')[0]
    weaponsAcquired = html_c.split('"weaponsAcquired":')[1].split(',')[0]
    weeklyKills = html_c.split('"weeklyKills":')[1].split(',')[0]
    weeklyWins = html_c.split('"weeklyWins":')[1].split(',')[0]
    wins = html_c.split('"wins":')[1].split(',')[0]
    rank_title, rank_icon = ranking(html_c.split('"rankPointsTitle":')[1].split(',')[0].replace('"',''),0)
    icon = [discord.File(directory + type_software + rank_icon),None]
    if platform == "Steam":
        icon[1] = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "steam.png")
        embed.set_author(icon_url="attachment://steam.png",name=message.content.split(" ")[1] + "님의 전적")
    elif platform == "Kakao":
        icon[1] = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "kakao.jpg")
        embed.set_author(icon_url="attachment://kakao.jpg",name=message.content.split(" ")[1] + "님의 전적")
    embed.set_thumbnail(url="attachment://" + rank_icon.replace("Assets" + type_software + "Rank" + type_software,""))
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
    data1 = "게임 수:" + str(int(wins) + int(top10s) + int(losses)) + "회\n승리:" + wins + "회\nTop10:" + top10s + "회\n패배:" + losses + "회\n승률:" + winper + "%\n일간 승리:" + dailyWins + "회\n주간 승리:" + weeklyWins + "회"
    data2 = "일간 킬 수" + dailyKills + "회\n주간 킬 수:" + weeklyKills + "회\n게임당 최다 킬 수:" +  maxKillStreaks + "회\n누적 킬 수:" +  kills + "회\n헤드샷:" +  headshotKills + "회(" + headshot_per + "%)\n어시스트:" +  assists + "회\nK/D:" +  KD + "\n차량 파괴:" +  vehicleDestroys + "회\n로드킬:" +  roadKills + "회\n최장 킬 거리:" +  str(round(float(longestKill),2)) + "m\n자살:" +  suicides + "회\n팀킬:" +  teamKills + "회"
    data3 = "플레이 시간:" + a_playtime + "\n이번 시즌 게임 접속일:" + days + "일\n최대 생존 시간:" + max_playtime + "\n평균 생존 시간:" + average_playtime + "\n치유:" + heals + "회\n부스트:" + boosts + "회"
    data4 = "종합 이동 거리:" + str(round(float(distance(walkDistance)) + float(distance(rideDistance)) + float(distance(swimDistance)),2)) + "km\n걸어간 거리:" + distance(walkDistance) + "km\n탑승 거리:" + distance(rideDistance) + "km\n평균 생존 시간:" + distance(swimDistance) + "km"
    data5 = "누적 입힌 피해:" + str(round(float(damageDealt),2)) + "\n무기 획득 횟수:" + weaponsAcquired + "회\nDBNO:" + dBNOs + "회\n소생:" + revives + "회"
    embed.set_thumbnail(url="attachment://" + rank_icon.replace("Assets" + type_software + "Rank" + type_software,""))
    embed.add_field(name="랭킹:",value=rank_title + "(" + rank_point + "점)",inline=False)
    embed.add_field(name="플레이 기록:",value=data1,inline=False)
    embed.add_field(name="전투 기록:",value=data2,inline=False)
    embed.add_field(name="게임 플레이:",value=data3,inline=False)
    embed.add_field(name="이동 거리:",value=data4,inline=False)
    embed.add_field(name="기타:",value=data5,inline=False)
    msg1 = await message.channel.send(files=icon,embed=embed)
    for i in range(3):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 개요 \U00000032\U0000FE0F\U000020E3 : 전적 정보 업데이트 \U00000033\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(3):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,user = await client.wait_for('reaction_add', check=check)
    if reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg1.delete()
        await msg2.delete()
        response1 = await requests.get(url,headers=header)
        if response1.status_code == 200:
            html = response1.text
        else:
            await response_num(response1,message,None,False)
            return
        html_nc = html.split('"' + game_mode + '":')[1].split('{')[1].split('}')[0]
        await profile_mode_status(message,platform,html_nc,url,game_mode,player_id)
        return
    elif reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        response1 = await requests.get(url,headers=header)
        if response1.status_code == 200:
            html = response1.text
        else:
            await response_num(response1,message,msg1,True)
            return
        await profile_mode(message,platform,True,msg1,html,url,player_id,game_mode)
        return

async def profile_mode(message,platform,update,update_msg,html,url,player_id,game_mode):
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    html_c = html.split('"' + game_mode + '":')[1].split('{')[1].split('}')[0]
    rank_point = str(round(float(html_c.split('"rankPoints":')[1].split(',')[0]),1))
    win = html_c.split('"wins":')[1].split('\n')[0]
    top10 = html_c.split('"top10s":')[1].split(',')[0]
    lose = html_c.split('"losses":')[1].split(',')[0]
    kills = html_c.split('"kills":')[1].split(',')[0]
    if int(lose) != 0:
        KD = str(round(int(kills) / int(lose),2))
    else:
        KD = str(round(int(kills) / 1,2))
    assists = html_c.split('"assists":')[1].split(',')[0]
    dBNOs = html_c.split('"dBNOs":')[1].split(',')[0]
    maxkill = html_c.split('"maxKillStreaks":')[1].split(',')[0]
    f_playtime = float(html_c.split('"timeSurvived":')[1].split(',')[0])
    playtime = datetime.datetime.fromtimestamp(f_playtime,timezone('UTC'))
    a_playtime = time_num(playtime)
    if int(kills) != 0:
        headshot = str(round(int(html_c.split('"headshotKills":')[1].split(',')[0]) / int(kills) * 100,1))
    else:
        headshot = "0"
    distance = str(round(float(html_c.split('"longestKill":')[1].split(',')[0]),2))
    rank_title, rank_icon = ranking(html_c.split('"rankPointsTitle":')[1].split(',')[0].replace('"',''),0)
    icon = [discord.File(directory + type_software + rank_icon),None]
    embed.set_thumbnail(url="attachment://" + rank_icon.replace("Assets" + type_software + "Rank" + type_software,""))
    embed.set_thumbnail(url="attachment://" + rank_icon.replace("Assets" + type_software + "Rank" + type_software,""))
    embed.add_field(name="랭킹:",value=rank_title + "(" + rank_point + "점)",inline=True)
    embed.add_field(name="승/탑/패:",value=win + "승 " + top10 + "탑 " + lose + "패",inline=True)
    embed.add_field(name="플레이타임:",value=a_playtime,inline=True)
    embed.add_field(name="킬(K/D):",value=kills + "회(" + KD + "점)",inline=True)
    embed.add_field(name="어시:",value=assists + "회",inline=True)
    embed.add_field(name="dBNOs:",value=dBNOs + "회",inline=True)
    embed.add_field(name="여포:",value=maxkill + "회",inline=True)
    embed.add_field(name="헤드샷:",value=headshot + "%",inline=True)
    embed.add_field(name="거리:",value=distance + "m",inline=True)
    if platform == "Steam":
        icon[1] = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "steam.png")
        embed.set_author(icon_url="attachment://steam.png",name=message.content.split(" ")[1] + "님의 전적")
    elif platform == "Kakao":
        icon[1] = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "kakao.jpg")
        embed.set_author(icon_url="attachment://kakao.jpg",name=message.content.split(" ")[1] + "님의 전적")
    if update:
        msg1 = await update_msg.channel.send(files=icon,embed=embed)
        await update_msg.delete()
    else:
        msg1 = await message.channel.send(files=icon,embed=embed)
    for i in range(4):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 상세정보 \U00000032\U0000FE0F\U000020E3 : 전적 정보 업데이트 \U00000033\U0000FE0F\U000020E3 :  종합 전적 \U00000034\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(3):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,user = await client.wait_for('reaction_add', check=check)
    if reaction.emoji == "\U00000034\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        return
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        await profile_total(message,platform,True,msg1,html,url,player_id)
        return
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        response1 = await requests.get(url,headers=header)
        if response1.status_code == 200:
            html_n = response1.text
        else:
            await response_num(response1,message,msg1,True)
            return
        await profile_mode(message,platform,True,msg1,html_n,url,player_id,game_mode)
        return
    elif reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg1.delete()
        await msg2.delete()
        await profile_mode_status(message,platform,html_c,url,game_mode,player_id)
        return
    return

async def profile_total(message,platform,update,update_msg,html,url,player_id):
    list_message = message.content.split(" ")
    embed = discord.Embed(color=0xffd619)
    if platform == "Kakao":
        file = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "kakao.jpg")
        embed.set_author(icon_url="attachment://kakao.jpg",name=list_message[1] + "님의 전적")
        game_mode = ["solo","duo","squad"]
        list_name = ["솔로(Solo)","듀오(Duo)","스쿼드(Squad)"]
        count = 3
    elif platform == "Steam":
        file = discord.File(directory + type_software + "Assets" + type_software + "Icon" + type_software + "steam.png")
        embed.set_author(icon_url="attachment://steam.png",name=list_message[1] + "님의 전적")
        game_mode = ["solo","duo","squad","solo-fpp","duo-fpp","squad-fpp"]
        list_name = ["솔로(Solo)","듀오(Duo)","스쿼드(Squad)","솔로 1인칭","듀오 1인칭","스쿼드 1인칭"]
        count = 6
    for i in range(count):
        html_c = html.split('"' + game_mode[i] + '":')[1].split('{')[1].split('}')[0]
        rank_point = str(round(float(html_c.split('"rankPoints":')[1].split(',')[0]),1))
        rank_title, rank_icon = ranking(html_c.split('"rankPointsTitle":')[1].split(',')[0].replace('"',''),0)
        win = html_c.split('"wins":')[1].split('\n')[0]
        top10 = html_c.split('"top10s":')[1].split(',')[0]
        lose = html_c.split('"losses":')[1].split(',')[0]
        kills = html_c.split('"kills":')[1].split(',')[0]
        if int(lose) != 0:
            KD = str(round(int(kills) / int(lose),2))
        else:
            KD = str(round(int(kills) / 1,2))
        embed.add_field(name=list_name[i] + ": ",value="**" + rank_title + "(" + rank_point + "점)**\n" + win + "승 " + top10 + "탑 " + lose + "패\n킬: " + kills + "회(" + KD + "점)",inline=True)
    if update:
        await update_msg.delete()
        msg1 = await message.channel.send(file=file,embed=embed)
    else:
        msg1 = await message.channel.send(file=file,embed=embed)
    for i in range(6):
        await msg1.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg2 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 솔로전적 \U00000032\U0000FE0F\U000020E3 : 듀오 전적 \U00000033\U0000FE0F\U000020E3 : 스쿼드 전적 \U00000034\U0000FE0F\U000020E3 : 최근 전투 내역 \U00000035\U0000FE0F\U000020E3 : 전적 정보 업데이트 \U00000036\U0000FE0F\U000020E3 : 메뉴 종료")
    author = message.author
    message_id = msg1.id
    def check(reaction, user):
        for i in range(6):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,user = await client.wait_for('reaction_add', check=check)
    if reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        await profile_mode(message,platform,True,msg1,html,url,player_id,"solo")
        return
    elif reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        await profile_mode(message,platform,True,msg1,html,url,player_id,"duo")
        return
    elif reaction.emoji == "\U00000033\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        await profile_mode(message,platform,True,msg1,html,url,player_id,"squad")
        return
    elif reaction.emoji == "\U00000034\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        season = url.replace("https://api.pubg.com/shards/steam/players/" + player_id + "/seasons/","")
        await matches(message,platform,0,msg1,player_id,season)
        return
    elif reaction.emoji == "\U00000035\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        response = await requests.get(url,headers=header)
        if response.status_code == 200:
            html = response.text
        else:
            await response_num(response,message,None,False)
            return
        await profile_total(message,platform,True,msg1,html,url,player_id)
        return
    elif reaction.emoji == "\U00000036\U0000FE0F\U000020E3":
        await msg1.clear_reactions()
        await msg2.delete()
        return
    return

async def profile(message,platform,perfix):
    list_message = message.content.split(" ")
    embed = discord.Embed(color=0xffd619)
    try:
        nickname = list_message[1]
        player_id = await player(nickname,message)
        if player_id == "False":
            return
    except:
        if platform == "Kakao":
            if list_message[0] == perfix + "카배":
                embed = discord.Embed(title="펍지봇 도움이",description="=카배 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "카배솔로":
                embed = discord.Embed(title="펍지봇 도움이",description="=카배솔로 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "카배듀오":
                embed = discord.Embed(title="펍지봇 도움이",description="=카배듀오 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "카배스쿼드":
                embed = discord.Embed(title="펍지봇 도움이",description="=카배스쿼드 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
        elif platform == "Steam":
            if list_message[0] == perfix + "스배":
                embed = discord.Embed(title="펍지봇 도움이",description="=스배 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "스배솔로":
                embed = discord.Embed(title="펍지봇 도움이",description="=스배솔로 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "스배듀오":
                embed = discord.Embed(title="펍지봇 도움이",description="=스배듀오 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
            elif list_message[0] == perfix + "스배스쿼드":
                embed = discord.Embed(title="펍지봇 도움이",description="=스배스쿼드 [닉네임] [시즌(선택)]\n닉네임을 작성해주시기 바랍니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                return
        else:
            embed = discord.Embed(title="에러",description="잘못된 인자가 들어왔습니다.", color=0xffd619)
            await message.channel.send(embed=embed)
            return
    finally:
        try:
            count = list_message[2]
            if len(count) < 2:
                season = "division.bro.official.pc-2018-0" + count
            else:
                season = "division.bro.official.pc-2018-" + count
        except:
            season = await top_season(message)
            if season == "False":
                return
    if platform == "Kakao":
        url = "https://api.pubg.com/shards/kakao/players/" + player_id + "/seasons/" + season
    else:
        url = "https://api.pubg.com/shards/steam/players/" + player_id + "/seasons/" + season
    response1 = await requests.get(url,headers=header)
    if response1.status_code == 200:
        html = response1.text
    else:
        await response_num(response1,message,None,False)
        return
    if platform == "Kakao":
        if list_message[0] == perfix + "카배":
            await profile_total(message,"Kakao",False,None,html,url,player_id)
            return
        elif list_message[0] == perfix + "카배솔로":
            await profile_mode(message,"Kakao",False,None,html,url,player_id,"solo")
            return
        elif list_message[0] == perfix + "카배듀오":
            await profile_mode(message,"Kakao",False,None,html,url,player_id,"duo")
            return
        elif list_message[0] == perfix + "카배스쿼드":
            await profile_mode(message,"Kakao",False,None,html,url,player_id,"squad")
            return
        elif list_message[0] == perfix + "카배매칭":
            await matches(message,"Kakao",0,None,None,player_id,season)
            return
        return
    elif platform == "Steam":
        if list_message[0] == perfix + "스배":
            await profile_total(message,"Steam",False,None,html,url,player_id)
            return
        elif list_message[0] == perfix + "스배솔로":
            await profile_mode(message,"Steam",False,None,html,url,player_id,"solo")
            return
        elif list_message[0] == perfix + "스배듀오":
            await profile_mode(message,"Steam",False,None,html,url,player_id,"duo")
            return
        elif list_message[0] == perfix + "스배스쿼드":
            await profile_mode(message,"Steam",False,None,html,url,player_id,"squad")
            return
        elif list_message[0] == perfix + "스배매칭":
            await matches(message,"Steam",0,None,None,player_id,season)
            return
        return


@client.event
async def on_ready(): 
    print("디스코드 봇 로그인이 완료되었습니다.")
    print("디스코드봇 이름:" + client.user.name)
    print("디스코드봇 ID:" + str(client.user.id))
    print("디스코드봇 버전:" + str(discord.__version__))
    print('------')
    await autopost(30)
    await client.change_presence(status=discord.Status.online)
    answer = ""
    total = 0
    for i in range(len(client.guilds)):
        answer = answer + str(i+1) + "번째: " + str(client.guilds[i]) + "(" + str(client.guilds[i].id) + "):"+ str(len(client.guilds[i].members)) +"명\n"
        total += len(client.guilds[i].members)
    print("방목록: \n" + answer + "방의 종합 멤버:" + str(total) + "명")

@client.event
async def on_message(message):
    author_id = message.author.mention.replace("<@","",).replace(">","").replace("!","")
    list_message = message.content.split(' ')
    if message.author == client.user or message.author.bot:
        return
    connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8')
    try:
        cur = connect .cursor()
        sql_prefix = "select * from SERVER_INFO where ID=" + str(message.guild.id)
        cur.execute(sql_prefix)
        cache = cur.fetchall()
        perfix = cache[0][1]
    except:
        perfix = "!="
    connect.close()
    if message.content.startswith(perfix + "카배"):
        log_info(message)
        if is_banned(author_id,message):
            return
        await profile(message,"Kakao",perfix)
        return
    if message.content.startswith(perfix + "스배"):
        log_info(message)
        if is_banned(author_id,message):
            return
        await profile(message,"Steam",perfix)
        return
    if message.content.startswith(perfix + '접두어') or message.content.startswith('!=접두어') :
        log_info(message)
        if is_banned(author_id,message):
            return
        if message.guild == None:
            embed = discord.Embed(title="접두어",description="DM에서는 접두어 기능을 사용하실수 없습니다.", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        try:
            mode = list_message[1]
        except:
            if perfix == "=":
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
            else:
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        else:
            connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8')
            cur = connect .cursor()
            if mode == "설정":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                try:
                    n_perfix = list_message[2]
                    if len(n_perfix) > 4 or len(list_message) > 3 or n_perfix.find('\t') != -1 or n_perfix.find('\n') != -1 :
                        if perfix == "=":
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                        else:
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                        await message.channel.send(embed=embed)
                        connect.close()
                        return
                except:
                    if perfix == "=":
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                    else:
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.commit()
                    connect.close()
                    return
                sql_T = "select EXISTS (select * from SERVER_INFO where ID=" + str(message.guild.id) + ") as success"
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    sql = "insert into SERVER_INFO(ID,PERFIX) values (%s, %s)"
                    cur.execute(sql,(message.guild.id,n_perfix))
                else:
                    sql = "update SERVER_INFO set PERFIX='" + n_perfix + "' where ID=" + str(message.guild.id)
                    cur.execute(sql)
                embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + n_perfix + "(명령어)으로 성공적으로 설정되었습니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.commit()
                connect.close()
            elif mode == "초기화":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                sql_T = "select EXISTS (select * from SERVER_INFO where ID=" + str(message.guild.id) + ") as success"
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    embed = discord.Embed(title="접두어",description="접두어가 이미 기본설정(!=)으로 되어 있습니다...", color=0xffd619)
                else:
                    sql = "update SERVER_INFO set PERFIX='!=' where ID=" + str(message.guild.id)
                    cur.execute(sql)
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)으로 성공적으로 초기화가 완료되었습니다.", color=0xffd619)
                    connect.commit()
                connect.close()
                await message.channel.send(embed=embed)
            elif mode == "정보":
                try:
                    sql_perfix = "select * from SERVER_INFO where ID=" + str(message.guild.id)
                    cur.execute(sql_perfix)
                    c_perfix = cur.fetchall()
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + str(c_perfix[0][1]) + "(명령어)입니다.", color=0xffd619)
                except:
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)입니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.close()
                return
            else:
                if perfix == "=":
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                else:
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                connect.close()
                await message.channel.send(embed=embed)
                return
    if message.content == perfix + "도움" or message.content == perfix + "help":
        log_info(message)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="도움말",color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
        embed.add_field(name="=스배 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 종합 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배솔로 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배듀오 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배스쿼드 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배솔로(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배듀오(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=스배스쿼드(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=카배 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 종합 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=카배솔로 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=카배듀오 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=카배스쿼드 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name="=서버상태:",value="배틀그라운드 서버 상태를 알려줍니다.",inline=False)
        await message.channel.send(embed=embed)
        return
    if message.content == perfix + "서버상태":
        log_info(message)
        if is_banned(author_id,message):
            return
        response = await requests.get("https://steamcommunity.com/app/578080")
        if response.status_code == 200:
            html = response.text
        else:
            embed = discord.Embed(title="에러",description=message.guild.name + "정보를 불러오기에 실패했습니다..", color=0xffd619)
            await message.channel.send(embed=embed)
            return
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
    if message.content.startswith(perfix + 'eval') and is_manager(author_id):
        log_info(message)
        if is_banned(author_id,message):
            return
        code =  message.content.replace(perfix + 'eval ','')
        if code == "" or code == perfix + "eval":
            embed = discord.Embed(title="에러!",description="내용을 적어주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        answer = eval(code)
        embed = discord.Embed(title="eval",description=answer, color=0xffd619)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + 'hellothisisverification'):
        log_info(message)
        if is_banned(author_id,message):
            return
        await message.channel.send("건유1019#0001(340373909339635725)")
        return
    if message.content == perfix + "ping":
        log_info(message)
        if is_banned(author_id,message):
            return
        now = datetime.datetime.utcnow()
        response_ping_c = now - message.created_at
        reading_ping = float(str(response_ping_c.seconds) + "." +  str(response_ping_c.microseconds))
        embed = discord.Embed(title="Pong!",description="클라이언트 핑상태: " + str(round(client.latency * 1000,2)) + "ms\n읽기 속도: " + str(round(reading_ping * 1000,2)) + "ms", color=0x00aaaa)
        msg = await message.channel.send(embed=embed)
        now = datetime.datetime.utcnow()
        response_ping_a = msg.created_at - now
        response_ping = float(str(response_ping_a.seconds) + "." +  str(response_ping_a.microseconds))
        embed = discord.Embed(title="Pong!",description="클라이언트 핑상태: " + str(round(client.latency * 1000,2)) + "ms\n읽기 속도: " + str(round(reading_ping * 1000,2)) + "ms\n출력 속도: " + str(round(response_ping * 1000,2)) + "ms", color=0x00aaaa)
        await msg.edit(embed=embed)
        return
    if message.content == perfix + '시스템':
        log_info(message)
        if is_banned(author_id,message):
            return
        data1 = str(psutil.cpu_percent(interval=None, percpu=False))
        data2 = str(psutil.virtual_memory().percent)
        data3 = str(psutil.disk_usage('/').percent)
        data4 = platform.system() + str(platform.release())
        data5 = psutil.virtual_memory()
        data6 = psutil.disk_usage('/')
        if platform.system() == "Linux":
            data7 = str(round(float(str(psutil.sensors_temperatures()).split('current=')[1].split(',')[0]),2))
        data8 = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        total_RAM,total_type_RAM = change_data(psutil.virtual_memory()[0])
        used_RAM,used_type_RAM = change_data(psutil.virtual_memory()[3])
        total_SSD,total_type_SSD = change_data(psutil.disk_usage('/')[0])
        used_SSD,used_type_SSD = change_data(psutil.disk_usage('/')[1])
        embed = discord.Embed(title="[시스템 정보]", color=0x00aaaa)
        embed.add_field(name="CPU:", value=data1 + "%", inline=True)
        embed.add_field(name="부팅시간:", value=data8, inline=True)
        embed.add_field(name="메모리:", value=data2 + "%(" + str(used_RAM) + str(used_type_RAM) + '/' + str(total_RAM) + str(total_type_RAM) + ')', inline=False)
        embed.add_field(name="저장공간:", value=data3 +"%(" + str(used_SSD) + str(used_type_SSD) + '/' + str(total_SSD) + str(total_type_SSD) + ')' , inline=False)
        embed.add_field(name="소프트웨어:", value=data4, inline=False)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + '블랙리스트 추가') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            mention_id = list_message[2]
        except:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0x00aaaa)
            await message.channel.send(embed=embed)
            return
        cache_data = mention_id.replace("<@","",).replace(">","").replace("!","")
        if is_manager(cache_data):
            embed = discord.Embed(title="에러!",description="관리자는 블랙리스트에 추가할수 없습니다!", color=0x00aaaa)
            await message.channel.send(embed=embed)
            return
        connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8') 
        cur = connect .cursor()
        sql_Black = "insert into BLACKLIST(ID) value(%s)"
        cur.execute(sql_Black,cache_data)
        connect.commit()
        connect.close()
        embed = discord.Embed(title="Blacklist!",description=mention_id + "가 블랙리스트에 추가되었습니다!", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + '블랙리스트 여부'):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            tester_id = list_message[2].replace("<@","",).replace(">","").replace("!","")
        except:
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
    if message.content.startswith(perfix + '블랙리스트 제거') and is_manager(author_id):
        log_info(message)
        try:
            mention_id = list_message[2]
        except:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0x00aaaa)
            await message.channel.send(embed=embed)
            return
        cache_data1 = mention_id.replace("<@","",).replace(">","").replace("!","")
        connect = pymysql.connect(host='192.168.0.10', user='PUBG_BOT', password='PASSW@RD!',db='PUBG_BOT', charset='utf8') 
        cur = connect .cursor()
        sql_delete = "delete from BLACKLIST where ID=%s"
        try:
            cur.execute(sql_delete,cache_data1)
        except:
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
    
client.run(token)