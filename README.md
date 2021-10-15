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
<a href="https://app.fossa.com/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT?ref=badge_shield" alt="FOSSA Status"><img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT.svg?type=shield"/></a>
    <img src="https://img.shields.io/badge/release_version-2.2-0080aa?style=flat" alt="Release" >
</p>

> **[Contect]**<br/>
> 해당 프로젝트에 대한 정해진 플랫폼 이외를 통하여 문의하는 것을 일체 금지합니다.<br/>
> 프로젝트에 관련된 질문은 Github의 [Issues](https://github.com/gunyu1019/PUBG-BOT/issues) 혹은 [포럼 서버](https://yhs.kr/PUBG_BOT/forum.html) 만을 이용해주시기 부탁드립니다.

# Introduce

한국어 기반의 배틀그라운드 전적을 알려주는 디스코드 봇입니다. 사용자의 전적과 매치 로그를 확인할 수 있습니다.
> (Developer Notes) Discord Introgation(Slash Command, Components)을 직접 구성하였습니다.
> [모듈 폴더](module) 내에 있는 `components.py`, `interaction.py`, `message.py`를 확인 해주시길 바랍니다.

> **안내 사항**:<br/>
> 이 디스코드 봇은 "빗금 명령어(Slash Command)"를 지원합니다.<br/>
> 디스코드의 새로운 기능 빗금 명령어 기능을 `/`을 통하여 체험해 보세요!<br/>
> <img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/slash_command_support.png?raw=true" width="50%" alt="slash_command_support">

### 전적 기능(/전적, !=전적)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command1.png?raw=true" width="50%" alt="command1"><br/>
전적 기능을 통하여 배틀그라운드 플레이어의 전적을 확인해보세요!
일반 모드와 경쟁 모드를 보다 편리하게 확인하실 수 있습니다. 특히 버튼 기능을 활용하여 특정 모드 전적을 세세히 확인할 수 있습니다.

### 매치 히스토리 기능(/매치, !=매치)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command2.png?raw=true" width="50%" alt="command2"><br/>
매치 히스토리 기능을 통하여 플레이 내역을 확인해보세요. 누구랑 팀원을 했는지, ~~누가 버스를 안탔는지,~~ 어디서 누구를 잡았는 지등의 다양한 정보를 제공합니다.

### 맵 기능(/<맵 이름>, !=<맵 이름>)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command3.png?raw=true" width="50%" alt="command3"><br/>
맵 기능을 활용하여 배틀그라운드 맵을 미리 확인하세요. 미리 지도를 확인하고 전략을 짜는 것도 하나의 전략이겠죠?

### 서버 정보 기능(/상태, !=상태)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/master/.github/command4.png?raw=true" width="50%" alt="command4"><br/>
서버 정보 기능을 활용하여 배틀그라운드 스팀 서버의 사용자 수를 확인해보세요. 사용자 수가 갑작스럽게 내려가거나, 흔히 알고있는 동접자 수보다 낮을때에는 점검 중이라는 것도 짐작할 수 있어요.

# Clone
본 프로젝트를 사용하기 위해서는 [라이센스](License)를 지킨다는 조건 아래에 사용이 가능합니다.

<table>
    <thead>
        <tr>
            <th>NAME</th>
            <th>VERSION</th>
            <th>TESTED</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Windows</td>
            <td>Windows 10 20H2</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>Raspbian</td>
            <td>Raspbian GNU/Linux 10</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Production)</td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.8.6</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.8.5</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Production)</td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.7.3</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2716.png">❌️</g-emoji>( ≤ v2.0 )</td>
        </tr>
            <tr>
            <td>MariaDB</td>
                <td>10.3.23-MariaDB</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji></td>
        </tr>
    </tbody>
</table>

* `v2.1` 버전 부터 `discord.py`의 요구 사항이 `Python3.8` 이상인 것을 반영하여 `Python3.8` 미만의 버전은 `v2.0` 까지만 사용이 가능합니다.

사용 전, 아래 과정을 거쳐주세요.
#### 1. MySQL에 `setup.sql` 문을 실행시켜주세요.
실행 전, 코드 안에 있는 `DISCORD BOT TOKEN`, `PUBG API TOKEN` 를 채워주세요.

#### 2. requirements.txt 안에 있는 모듈을 모두 설치해 주세요.
PUBG BOT이 정상적으로 구동되기 위해 필요한 파일입니다. 꼭 설치해 주세요.
```commandline
pip install -r requirements.txt
```

#### 3. config 파일을 설정해주세요.
[config_example.ini](config/config_example.ini) 를 `config.ini`로 변경한 후, 파일 내에 설정을 해주세요.
```commandline
cd PUBG_BOT
mv config/config_example.ini config/config.ini
```

설정 파일을 올바르게 수정해주세요.
*  `MySQL1`, `MySQL2` 를 굳이 다 채우지 않으셔도 됩니다. 
   `MySQL1`이(가) 우선 실행됩니다. 
   그러나 `MySQL1`이 정상적으로 작동하지 않을 경우, `MySQL2`가 실행됩니다.
* `token`, `PUBG_API`를 채우실 필요는 없습니다. (MySQL 값을 채우지 않았을 때에만 작동합니다.)
* `inspection` 값을 활성화 하시면 점검 모드가 활성화 됩니다.

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


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT?ref=badge_large)

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

아래의 파일들은 펍지 주식회사(이하 "회사")가 소유권(지식재산권)을 보유하고있습니다. 해당 디스코드 봇은 [이용약관](https://developer.pubg.com/tos)
과 [이용자 제작 콘텐츠 규칙](https://asia.battlegrounds.pubg.com/ko/player-created-content/) 준수하였습니다.

* [assets/Icon](assets/Icon)
* [assets/Insignias](assets/Insignias)
* [assets/Maps](assets/Maps)
* [assets/*](assets)
