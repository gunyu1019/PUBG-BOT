<p align="center">
    <img src="https://user-images.githubusercontent.com/16767890/127808428-f1cb3adb-f159-43d1-bc33-1a0f6db182bc.png" width="30%"/>
</p>
<h1 align="center">PUBG BOT</h1>
<p align="center">
    <a href="https://www.codacy.com/gh/gunyu1019/PUBG-BOT/dashboard"><img src="https://app.codacy.com/project/badge/Grade/8c90b5a8f40e46a097ce2c5dd099d9e0" /></a>
    <a href="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/overview/master"><img src="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/badge/v1.2" /></a>
    <img src="https://img.shields.io/badge/python-3.8-3776AB?style=flat&logo=python&logoColor=ffffff" />
    <img src="https://img.shields.io/badge/release_version-1.1-0080aa?style=flat" />
    <img src="https://img.shields.io/badge/PLT_version-2.0-0080aa?style=flat" />
</p>

# Introduce
한국어 기반의 배틀그라운드 전적을 알려주는 디스코드 봇입니다. 
사용자의 전적과 매치 로그를 확인할 수 있습니다.
> (Developer Notes) Discord Introgation(Slash Command, Components)을 직접 구성하였습니다.
> [모듈 폴더](module) 내에 있는 `components.py`, `interaction.py`, `message.py`를 확인 해주시길 바랍니다.

# Structure
PUBG BOT의 구성은 다음과 같습니다.
* [assets](assets) : PUBG BOT의 에셋 파일입니다.
* [cogs](cogs) : `discord.py`에서 제공하는 `cogs`입니다.
* [commands](commands) : PUBG BOT 에서 직접 구성한 `cogs` 체계입니다. 빗금명령어와 일반명령어를 동시에 사용할 수 있습니다.
* [config](config) : PUBG BOT의 설정 파일입니다.
* [module](module) : PUBG BOT이 구성되기 위한 "자체 모듈"입니다. `pubgpy`와 Slash Command, Components 를 호환하기 위한 코드가 들어 있습니다.
* [process](process) : 처리 과정의 소스코드 입니다. 상호작용과 주요 기능의 메세지 출력은 해당 코드에서 이루어 집니다.
* [utils](utils) : PUBG BOT이 정상적으로 구동되기 위한 모듈 입니다.

# License
프로젝트의 라이센스의 구성은 다음과 같습니다.

### MIT License
아래의 파일들은 MIT License가 적용됩니다.
* [module/*](module)
* [PUBGpy](module/pubgpy)

### GNU General Public License v3.0
아래의 파일들은 GNU(General Public License v3.0)가 적용됩니다.
* [assets/_resource](assets/_resource)
* [cogs/*](cogs)
* [commands/*](commands)
* [data/*](data)
* [utils/*](utils)
* [main.py](main.py)

### [PLAYERUNKNOWN’S BATTLEGROUNDS](https://github.com/pubg/api-assets) 저작권
아래의 파일들은 펍지 주식회사(이하 "회사")가 소유권(지식재산권)을 보유하고있습니다.
해당 디스코드 봇은 [이용약관](https://developer.pubg.com/tos) 과 [이용자 제작 콘텐츠 규칙](https://asia.battlegrounds.pubg.com/ko/player-created-content/) 준수하였습니다.
* [assets/Icon](assets/Icon)
* [assets/Insignias](assets/Insignias)
* [assets/Maps](assets/Maps)
* [assets/*](assets)
