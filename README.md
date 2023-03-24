<p align="center">
    <img src="https://github.com/gunyu1019/PUBG-BOT/blob/main/.github/PUBG_BOT.png?raw=true" width="30%" alt="PUBG BOT"/>
</p>
<h1 align="center">PUBG BOT</h1>
<p align="center">
    <img src="https://koreanbots.dev/api/widget/bots/status/704683198164238446.svg?style=classic" alt="Status" >
    <img src="https://koreanbots.dev/api/widget/bots/servers/704683198164238446.svg?icon=false&style=classic" alt="Server" >
    <a href="https://www.codacy.com/gh/gunyu1019/PUBG-BOT/dashboard">
        <img src="https://app.codacy.com/project/badge/Grade/8c90b5a8f40e46a097ce2c5dd099d9e0" alt="Codacy" >
        </a>
    <a href="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/overview/main">
        <img src="https://www.codefactor.io/repository/github/gunyu1019/pubg-bot/badge/main" alt="CodeFactor" >
    </a>
<a href="https://app.fossa.com/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT?ref=badge_shield" alt="FOSSA Status"><img src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT.svg?type=shield"/></a>
    <img src="https://img.shields.io/badge/release_version-2.3.2-0080aa?style=flat" alt="Release" >
</p>

# Introduce

한국어 기반의 배틀그라운드 전적을 알려주는 디스코드 봇입니다. 사용자의 전적과 매치 로그를 확인할 수 있습니다.

### 전적 기능(/전적)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/main/.github/command1.png?raw=true" width="50%" alt="command1"><br/>
전적 기능을 통하여 배틀그라운드 플레이어의 전적을 확인해보세요!
일반 모드와 경쟁 모드를 보다 편리하게 확인하실 수 있습니다. 특히 버튼 기능을 활용하여 특정 모드 전적을 세세히 확인할 수 있습니다.

### 매치 히스토리 기능(/매치)

<img src="https://github.com/gunyu1019/PUBG-BOT/blob/main/.github/command2.png?raw=true" width="50%" alt="command2"><br/>
매치 히스토리 기능을 통하여 플레이 내역을 확인해보세요. 누구랑 팀원을 했는지, ~~누가 버스를 안탔는지,~~ 어디서 누구를 잡았는 지등의 다양한 정보를 제공합니다.

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
            <td>Windows 11 22H2</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>Mac</td>
            <td>Mac OS Ventura</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Development)</td>
        </tr>
        <tr>
            <td>Raspbian</td>
            <td>Raspbian GNU/Linux 10</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji> (Production)</td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.11.2</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2714.png">✔️</g-emoji></td>
        </tr>
        <tr>
            <td>Python</td>
            <td>v3.8.6</td>
            <td><g-emoji class="g-emoji" alias="heavy_check_mark" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/2716.png">❌️</g-emoji>( ≤ v3.0 )</td>
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
* `v3.0` 버전 부터 `discord.extension.interaction`의 요구 사항이 `Python3.10` 이상인 것을 반영하여 `Python3.11` 에 따라 제작되었습니다.

사용 전, 아래 과정을 거쳐주세요.
#### 1. MySQL에 `setup.sql` 문을 실행시켜주세요.
(데이터베이스 구성에 대한 내용은 아직 작성되지 않았습니다.)

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

# Structure

PUBG BOT의 구성은 다음과 같습니다.

* [assets](assets) : PUBG BOT의 에셋 파일입니다.
* [cogs](cogs) : `discord.ext.interaction`에서 제공하는 `cogs`입니다. 주로 명령어를 처리합니다.
* [config](config) : PUBG BOT의 설정 파일입니다.
* [models](models) : PUBG BOT의 데이터 모델 클래스 입니다.
* [module](module) : PUBG BOT이 구성되기 위한 "자체 모듈"입니다. `pubgpy`가 포함되어 있습니다.
* [process](process) : 처리 과정의 소스코드 입니다. 상호작용과 주요 기능의 메세지 출력은 해당 코드에서 이루어 집니다.
* [utils](utils) : PUBG BOT이 정상적으로 구동되기 위한 유틸리티 파일 입니다.

# License
프로젝트의 라이센스의 구성은 다음과 같습니다.


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fgunyu1019%2FPUBG-BOT?ref=badge_large)

### MIT License

아래의 파일들은 MIT License가 적용됩니다.

* [PUBGpy](module/pubgpy)

### GNU General Public License v3.0

아래의 파일들은 GNU(General Public License v3.0)가 적용됩니다.

* [assets/_resource](assets/_resource)
* [cogs/*](cogs)
* [models/*](models)
* [module/*](module)
* [utils/*](utils)
* [main.py](main.py)
