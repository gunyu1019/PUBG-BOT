import urllib.request
import requests
import os

start_url = "https://opgg-pubg-static.akamaized.net/assets"
cut_url = 'style="background-image: url(https://opgg-pubg-static.akamaized.net/assets'
directory = os.path.dirname(os.path.abspath(__file__))
html = requests.get("https://pubg.op.gg/weapons").text
a_name = ""
for i in range(36):
    url = html.split(cut_url)[i+1].split('?')[0]
    #name = html.split('https://opgg-pubg-static.akamaized.net/assets/assets/item/weapon/')[i+1].split('?')[0].split('/')[1]
    name = html.split('<span class="weapons__txt">')[i+1].split('</span>')[0].replace('\n','').replace(' ','').replace('\t','')
    a_name = a_name + name + "\n"
    print(start_url + url + "설치합니다.")
    urllib.request.urlretrieve(start_url + url, directory + "\\" + name)
    print(str(i) + "번째 설치 완료.")
print(a_name)
