"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .models import BaseModel, PUBGModel
from .enums import Platforms, get_enum


class Weapon(PUBGModel):
    """ Weapon Mastery contains weapon summaries for the lifetime of a player

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the leaderboard response
    type : str
        Identifier for this object type
    platform : str
        Type of platform
    latest_match : str
        Match ID of the last completed match that was played
    summaries : list of WeaponSummary
        Match ID of the last completed match that was played
    """

    def __init__(self, data):
        self.data = data

        self.type: str = self.data.get("type", "weaponMasterySummary")
        self.id: str = self.data.get("id")

        super().__init__(self)

        # attributes
        attributes = self.data.get("attributes")
        self.platform: Platforms = get_enum(Platforms, attributes.get("platform"))
        self.latest_match: str = attributes.get("latestMatchId")

        self.summaries = list()
        summaries = attributes.get("weaponSummaries")
        for x in summaries.keys():
            self.summaries.append(WeaponSummary(x))

    def __repr__(self):
        return "Weapon(id='{}', type='{}', platform='{}', latest_match='{}')".format(
            self.id, self.type, self.platform, self.latest_match)

    def __str__(self):
        return self.__repr__()


class WeaponSummary(BaseModel):
    """ Weapon summary for each weapon

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    xp : int
        Total amount of XP earned for this weapon
    level : int
        Current level of this weapon
    tier : int
        Current tier of this weapon
    most_defeats : int
        Most defeats in a single match
    defeats : int
        Total number of defeats in their career
    most_damage : float
        Most damage that the player did in a single match
    damage : float
        Total damage that the player has done in their career
    most_headshots : float
        Most headshots that the player did in a single match
    headshots : int
        Total headshots that the player has done in their career
    longest_defeat : float
        Longest distance that the player got a defeat for
    long_range_defeat : int
        Number of long range defeats for the player
    kills : int
        Total number of kills for the player
    most_kills : int
        Most kills for a player in a single match
    groggies : int
        Total number of times that the player has caused another player to become groggy during their career
    most_groggies : int
        Highest number of times that the player has caused another player to become groggy during a match
    medal : list of Medal
        All of the medals received for this weapon
    """

    def __init__(self, data):
        self.data = data
        super().__init__(data)

        self.xp: int = data.get("XPTotal", 0)
        self.level: int = data.get("LevelCurrent", 0)
        self.tier: int = data.get("TierCurrent", 0)

        # Stats
        stats = self.data.get("StatsTotal")
        self.most_defeats: int = stats.get("MostDefeatsInAGame", 0)
        self.defeats: int = stats.get("Defeats", 0)
        self.most_damage: float = stats.get("MostDamagePlayerInAGame", 0.0)
        self.damage: float = stats.get("DamagePlayer", 0.0)
        self.most_headshots: float = stats.get("MostHeadShotsInAGame", 0.0)
        self.headshots: int = stats.get("HeadShots", 0)
        self.longest_defeat: float = stats.get("LongestDefeat", 0.0)
        self.long_range_defeat: int = stats.get("LongRangeDefeats", 0)
        self.kills: int = stats.get("Kills", 0)
        self.most_kills: int = stats.get("MostKillsInAGame", 0)
        self.groggies: int = stats.get("Groggies", 0)
        self.most_groggies: int = stats.get("MostGroggiesInAGame", 0)

        self.medal = list()
        for i in self.data.get("Medals"):
            self.medal.append(Medal(i))

    def __repr__(self):
        return "WeaponSummary(xp={}, level={}, tier={}, most_defeats={}, defeats={}, most_damage={}, damage={}, " \
               "most_headshots={}, headshots={}, longest_defeat={}, kills={}, most_kills={}, groggies={}, " \
               "most_groggies={}) ".format(self.xp, self.level, self.tier, self.most_defeats, self.defeats,
                                           self.most_damage, self.damage, self.most_headshots, self.headshots,
                                           self.longest_defeat, self.kills, self.most_kills, self.groggies,
                                           self.most_groggies)

    def __str__(self):
        return self.__repr__()


class Medal(BaseModel):
    """ All of the medals received for this weapon

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        Name of the medal
    count : int
        Number of times that the player received the medal
    """

    def __init__(self, data):
        self.data = data

        super().__init__(data)
        self.id: str = self.data.get("MedalId")
        self.count: int = self.data.get("Count")

    def __repr__(self):
        return "Medal(id='{}', count={})".format(self.id, self.count)

    def __str__(self):
        return self.__repr__()


class Survival(PUBGModel):
    """ Survival Mastery contains survival mastery data for a player

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        Player ID (also known as account ID)
    type : str
        Identifier for this object type
    xp : int
        Survival Mastery experience points
    level : int
        Survival Mastery level
    round_played : int
        Number of matches played that count toward Survival Mastery
    last_match : str
        Match ID of the last completed match that was played
    air_drops : Stats
        Number of air drops called
    damage_dealt : Stats
        Total amount of damage dealt to other players
    damage_taken : Stats
        Total amount of damage taken
    swimming : Stats
        Total distance travelled by swimming
    vehicle : Stats
        Total distance travelled by vehicle
    foot : Stats
        Total distance travelled on foot
    distance : Stats
        Total distance travelled by foot, swimming, and vehicle
    healed : Stats
        Total amount healed
    hot_drop : Stats
        Number of times landing in a hot drop location
    enemy_crates : Stats
        Number of enemy crates looted
    position : Stats
        Match placement
    revived : Stats
        Number of times revived
    teammates_revived : Stats
        Number of times reviving another player
    time_survived : Stats
        Total time survived
    throwable : Stats
        Number of throwables thrown
    top10 : Stats
        Number of times placing in the top 10
    """

    def __init__(self, data):
        self.data = data

        self.type: str = self.data.get("type", "survivalMasterySummary")
        self.id: str = self.data.get("id")
        super().__init__(self)

        attributes = self.data.get("attributes")
        self.xp: int = attributes.get("xp", 0)
        self.level: int = attributes.get("level", 0)
        self.round_played: int = attributes.get("totalMatchesPlayed", 0)
        self.last_match: str = attributes.get("latestMatchId")

        stats = attributes.get("stats")
        self.air_drops = Stats(stats.get("airDropsCalled"))
        self.damage_dealt = Stats(stats.get("damageDealt"))
        self.damage_taken = Stats(stats.get("damageTaken"))
        self.swimming = Stats(stats.get("distanceBySwimming"))
        self.vehicle = Stats(stats.get("distanceByVehicle"))
        self.foot = Stats(stats.get("distanceByFoot"))
        self.distance = Stats(stats.get("distanceTotal"))
        self.healed = Stats(stats.get("healed"))
        self.hot_drop = Stats(stats.get("hotDropLandings"))
        self.enemy_crates = Stats(stats.get("enemyCratesLooted"))
        self.position = Stats(stats.get("position"))
        self.revived = Stats(stats.get("revived"))
        self.teammates_revived = Stats(stats.get("teammatesRevived"))
        self.time_survived = Stats(stats.get("timeSurvived"))
        self.throwable = Stats(stats.get("throwablesThrown"))
        self.top10 = Stats(stats.get("top10"))

    def __repr__(self):
        return "Survival(id='{}', type='{}', xp={}, level={}, round_played='{}' last_match='{}'".format(
                self.id, self.type, self.xp, self.level, self.round_played, self.last_match)

    def __str__(self):
        return self.__repr__()


class Stats(BaseModel):
    """ Model for stats values from Survival Mastery.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    total : int
        Career total
    average : int
        Career average
    career : int
        Career best
    last_match : int
        Value in last match
    """

    def __init__(self, data):
        super().__init__(data)
        self.data = data

        self.total: int = self.data.get("total", 0)
        self.average: int = self.data.get("average", 0)
        self.career: int = self.data.get("careerBest", 0)
        self.last_match: int = self.data.get("lastMatchValue", 0)

    def __repr__(self):
        return "Stats(total={}, average={} career={} last_match={})".format(
            self.total, self.average, self.career, self.last_match)

    def __str__(self):
        return self.__repr__()
