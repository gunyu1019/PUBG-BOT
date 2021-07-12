from enum import Enum


class Platforms(Enum):
    """Platforms supported"""
    STEAM = "steam"
    KAKAO = "kakao"
    XBOX = "xbox"
    PLAYSTATION = "psn"
    STADIA = "stadia"

    def __str__(self):
        return self.name


class Region(Enum):
    """Region supported"""
    AS = 'as'
    EU = 'eu'
    KAKAO = 'kakao'
    KRJP = 'krjp'
    NA = 'na'
    OC = 'oc'
    SA = 'sa'
    SEA = 'sea'
    JP = 'jp'
    RU = 'ru'
    TOURNAMENT = 'pc-tournament'

    def __str__(self):
        return self.name


class GameMode(Enum):
    """GameMode"""
    solo = "solo"
    duo = "duo"
    squad = "squad"
    solo_fpp = "solo-fpp"
    duo_fpp = "duo-fpp"
    squad_fpp = "squad-fpp"


class MatchType(Enum):
    """Game Match Type"""
    arcade = "arcade"
    custom = "custom"
    event = "event"
    official = "official"
    training = "training"


class MapName(Enum):
    """Game Map Name"""
    erangel = "Baltic_Main"
    paramo = "Chimera_Main"
    miramar = "Desert_Main"
    vikendi = "DihorOtok_Main"
    erangel_old = "Erangel_Main"
    haven = "Heaven_Main"
    camp_jackal = "Range_Main"
    sanhok = "Savage_Main"
    karakin = "Summerland_Main"


class SeasonStats(Enum):
    """Season Status"""
    progress = "progress"
    prepare = "prepare"
    closed = "closed"


class DeathType(Enum):
    """Death Type"""
    alive = "alive"
    kill = "byplayer"
    zone = "byzone"
    suicide = "suicide"
    logout = "logout"


def get_enum(cls, val):
    enum_val = [i for i in cls if i.value == val]
    if len(enum_val) == 0:
        return val
    return enum_val[0]
