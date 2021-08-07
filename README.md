<p align="center">
    <img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/PUBG_BOT.png?raw=true" width="30%" alt="PUBG BOT"/>
</p>
<h1 align="center">PUBG BOT</h1>
<p align="center">
    <img src="https://koreanbots.dev/api/widget/bots/status/704683198164238446.svg?style=classic" alt="Status" >
    <img src="https://koreanbots.dev/api/widget/bots/servers/704683198164238446.svg?icon=false&style=classic" alt="Server" >
    <a href="https://www.codacy.com/gh/gunyu1019/PUBG-BOT/dashboard">
        <img src="https://app.codacy.com/project/badge/Grade/8c90b5a8f40e46a097ce2c5dd099d9e0" alt="Codacy" >
        </a>
    <a href="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/overview/master">
        <img src="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/badge/master" alt="CodeFactor" >
    </a>
    <img src="https://img.shields.io/badge/release_version-2.0-0080aa?style=flat" alt="Release" >
</p>

# Introduce
한국어 기반의 배틀그라운드 전적을 알려주는 디스코드 봇입니다. 
사용자의 전적과 매치 로그를 확인할 수 있습니다.
> (Developer Notes) Discord Introgation(Slash Command, Components)을 직접 구성하였습니다.
> [모듈 폴더](module) 내에 있는 `components.py`, `interaction.py`, `message.py`를 확인 해주시길 바랍니다.

> **안내 사항**:<br/>
> 이 디스코드 봇은 "빗금 명령어(Slash Command)"를 지원합니다.<br/>
> 디스코드의 새로운 기능 빗금 명령어 기능을 `/`을 통하여 체험해 보세요!<br/>
> <img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/slash_command_support.png?raw=true" width="50%" alt="slash_command_support">

### 전적 기능(/전적, !=전적)
<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command1.png?raw=true" width="50%" alt="command1"><br/>
전적 기능을 통하여 배틀그라운드 플레이어의 전적을 확인해보세요!
일반 모드와 경쟁 모드를 보다 편리하게 확인하실 수 있습니다.
특히 버튼 기능을 활용하여 특정 모드 전적을 세세히 확인할 수 있습니다.

### 매치 히스토리 기능(/매치, !=매치)
<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command2.png?raw=true" width="50%" alt="command2"><br/>
매치 히스토리 기능을 통하여 플레이 내역을 확인해보세요. 
누구랑 팀원을 했는지, ~~누가 버스를 안탔는지,~~ 어디서 누구를 잡았는 지등의 다양한 정보를 제공합니다.

### 맵 기능(/<맵 이름>, !=<맵 이름>)
<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command3.png?raw=true" width="50%" alt="command3"><br/>
맵 기능을 활용하여 배틀그라운드 맵을 미리 확인하세요.
미리 지도를 확인하고 전략을 짜는 것도 하나의 전략이겠죠?

### 서버 정보 기능(/상태, !=상태)
<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command4.png?raw=true" width="50%" alt="command4"><br/>
서버 정보 기능을 활용하여 배틀그라운드 스팀 서버의 사용자 수를 확인해보세요.
사용자 수가 갑작스럽게 내려가거나, 흔히 알고있는 동접자 수보다 낮을때에는 점검 중이라는 것도 짐작할 수 있어요.

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
