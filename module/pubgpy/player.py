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

from .season import Season
from .models import BaseModel, PUBGModel
from .mastery import Weapon, Survival
from .enums import get_enum, Platforms

from typing import Union


class Player(PUBGModel):
    """ Player objects contain information about a player and a list of their recent matches (up to 14 days old).

    Notes
    -----
    player objects are specific to platform shards.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    client :
        Contains PUBGpy's main client class.
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the player response
    type : str
        Identifier for this object type
    name : str
        Name of Player
    shard : Platforms
        Type of shard ID
    title : str
        Identifies the studio and game
    stats : Stats, optional
        Player Information
    patch_version : str, optional
        Version of the game
    rank : str, optional
        One of the values returned from the leaderboard
    assets : Any, optional
        Player's assests
    matches : list
        A list of match ids.
    """
    def __init__(self, client, data):
        self.data = data
        self.client = client

        self.id = self.data.get("id")
        self.type = self.data.get("type", "Player")
        super().__init__(self)

        # Attributes
        self.name = self.data.get("attributes", {}).get("name")
        self.shard = get_enum(Platforms, self.data.get("attributes", {}).get("shardId"))
        self.title = self.data.get("attributes", {}).get("titleId")
        self.stats = Stats(self.data.get("attributes", {}).get("stats"))
        self.patch_version = self.data.get("attributes", {}).get("patchVersion")
        self.rank = self.data.get("attributes", {}).get("rank")

        # relationships
        self.assets = self.data.get("relationships", {}).get("assets", {}).get('data')
        self.matches = [_.get('id') for _ in self.data.get("relationships", {}).get("matches", {}).get('data', [])]

    def __dict__(self):
        return self.data

    def __repr__(self):
        return "Player(id='{}', name='{}', type='{}')".format(self.id, self.name, self.type)

    def __str__(self):
        return self.name

    async def season_stats(self, season: Union[Season, str] = None):
        """
        Get season information for a single player.

        Parameters
        ----------
        season : `Season` or `str`
            Contains season class.

        Returns
        -------
        GameModeReceive :
            Includes all information about general games by season according to game mode.
        """
        if season is None:
            season_fp = await self.client.current_season()
            season = season_fp.id
        elif isinstance(season, Season):
            season = season.id
        path = "/players/{}/seasons/{}".format(self.id, season)
        resp = await self.client.requests.get(path=path)
        return GameModeReceive(resp.get("data", {}).get("attributes", {}).get("gameModeStats", {}), SeasonStats)

    async def ranked_stats(self, season: Union[Season, str] = None):
        """
        Get ranked stats for a single player.

        Parameters
        ----------
        season : `Season` or `str`
            Contains season class.

        Returns
        -------
        GameModeReceive :
            Includes all information about ranked games by season according to game mode.
        """
        if season is None:
            season_fp = await self.client.current_season()
            season = season_fp.id
        elif isinstance(season, Season):
            season = season.id
        path = "/players/{}/seasons/{}/ranked".format(self.id, season)
        resp = await self.client.requests.get(path=path)
        print(resp)
        return GameModeReceive(resp.get("data", {}).get("attributes", {}).get("rankedGameModeStats", {}), RankedStats)

    async def lifetime_stats(self):
        """
        Get lifetime stats for a single player.

        Returns
        -------
        GameModeReceive :
            Includes all information about lifetime games by season according to game mode.
        """
        path = "/players/{}/seasons/lifetime".format(self.id)
        resp = await self.client.requests.get(path=path)
        return GameModeReceive(resp.get("data", {}).get("attributes", {}).get("gameModeStats", {}), SeasonStats)

    async def match(self, position: int = 0):
        """
        Get a single match.

        Notes
        -----
        Authorization is not required endpoint because it is not rate-limited.

        Parameters
        ----------
        position : int
            Gets the location of the inquired player's match list. It must be above zero.

        Returns
        -------
        Matches :
            Contains classes for Matches.

        Raises
        ------
        IndexError :
            List index out of Match List
        """
        if position > len(self.matches):
            raise IndexError("list index out of Match List")
        return await self.client.matches(match_id=self.matches[position])

    async def weapon(self):
        """
        Get weapon mastery information for a single player

        Returns
        -------
        Weapon :
            Contains classes for Weapon mastery.
        """
        path = "/players/{}/weapon_mastery".format(self.id)
        resp = await self.client.requests.get(path=path)
        return Weapon(resp)

    async def survival(self):
        """
        Get survival mastery information for a single player

        Returns
        -------
        Survival :
            Contains classes for Survival mastery.
        """
        path = "/players/{}/survival_mastery".format(self.id)
        resp = await self.client.requests.get(path=path)
        return Survival(resp)


class SeasonStats(BaseModel):
    """ Game Mode stats objects contain a player's aggregated stats for a game mode in the context of a season.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    assists : int
        Number of enemy players this player damaged that were killed by teammates
    boosts : int
        Number of boost items used
    dbnos : int
        Number of enemy players knocked
    daily_kills : int
        Number of kills during the most recent day played.
    daily_wins : int
        Number of wins during the most recent day played.
    damage_dealt : float
        Total damage dealt. Note: Self inflicted damage is subtracted
    days : int
        Number of Played per day
    headshot_kills : int
        Number of enemy players killed with headshots
    heals : int
        Number of healing items use
    kills : int
        Number of enemy players killed
    longest_kill : float
        Number of Maximum Sniper Range
    longest_time_survived : float
        Number of Longest time survived in a match
    losses : int
        Number of matches lost
    max_kill_streaks : int
        Number of Max Kill Streak
    most_survival_time : float
        Number of Average Survival Time
    revives : int
        Number of times this player revived teammates
    ride_distance : float
        Total distance traveled in vehicles measured in meters
    road_kills : int
        Number of kills while in a vehicle
    round_most_kills : int
        Highest number of kills in a single match
    rounds_played : int
        Number of matches played
    suicides : int
        Number of self-inflicted deaths
    swim_distance : float
        Total distance traveled while swimming measured in meters
    team_kills : int
        Number of times this player killed a teammate
    time_survived : float
        Total time survived
    top10s : int
        Number of times this player made it to the top 10 in a match
    vehicle_destroys : int
        Number of vehicles destroyed
    walk_distance : float
        Total distance traveled on foot measured in meters
    weapons_acquired : int
        Number of weapons picked up
    weekly_kills : int
        Number of kills during the most recent week played
    weekly_wins : int
        Number of wins during the most recent week played.
    wins : int
        Number of matches won
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.data = data

        self.assists: int = data.get("assists", 0)
        self.boosts: int = data.get("boosts", 0)
        self.dbnos: int = data.get("dBNOs", 0)
        self.daily_kills: int = data.get("dailyKills", 0)
        self.daily_wins: int = data.get("dailyWins", 0)
        self.damage_dealt: float = data.get("damageDealt", 0.0)
        self.days: int = data.get("days", 0)
        self.headshot_kills: int = data.get("headshotKills", 0)
        self.heals: int = data.get("heals", 0)
        self.kills: int = data.get("kills", 0)
        self.longest_kill: float = data.get("longestKill", 0.0)
        self.longest_time_survived: float = data.get("longestTimeSurvived", 0.0)
        self.losses: int = data.get("losses", 0)
        self.max_kill_streaks: int = data.get("maxKillStreaks", 0)
        self.most_survival_time: float = data.get("mostSurvivalTime", 0.0)
        self.revives: int = data.get("revives", 0)
        self.ride_distance: float = data.get("rideDistance", 0.0)
        self.road_kills: int = data.get("roadKills", 0)
        self.round_most_kills: int = data.get("roundMostKills", 0)
        self.rounds_played: int = data.get("roundsPlayed", 0)
        self.suicides: int = data.get("suicides", 0)
        self.swim_distance: float = data.get("swimDistance", 0.0)
        self.team_kills: int = data.get("teamKills", 0)
        self.time_survived: float = data.get("timeSurvived", 0.0)
        self.top10s: int = data.get("top10s", 0)
        self.vehicle_destroys: int = data.get("vehicleDestroys", 0)
        self.walk_distance: float = data.get("walkDistance", 0.0)
        self.weapons_acquired: int = data.get("weaponsAcquired", 0)
        self.weekly_kills: int = data.get("weeklyKills", 0)
        self.weekly_wins: int = data.get("weeklyWins", 0)
        self.wins: int = data.get("wins", 0)

    def __repr__(self):
        return "SeasonStats(assists={}, boosts={}, dBNOs={} daily_kills={} daily_wins={} damage_dealt={} " \
               "days={} headshot_kills={} heals={} kills={} longest_kill={} longest_time_survived={} " \
               "losses={} max_kill_streaks={} revives={} ride_distance={} road_kills={}" \
               "round_most_kills={} rounds_played={} suicides={} swim_distance={} team_kills={} " \
               "time_survived={} top10s={} vehicle_destroys={} walk_distance={} weapons_acquired={} " \
               "weekly_wins={} wins={})".format(
                self.assists, self.boosts, self.dbnos, self.daily_kills, self.daily_wins, self.damage_dealt, self.days,
                self.headshot_kills, self.heals, self.kills, self.longest_kill, self.longest_time_survived, self.losses,
                self.max_kill_streaks, self.revives, self.ride_distance, self.road_kills, self.round_most_kills,
                self.rounds_played, self.suicides, self.swim_distance, self.team_kills, self.time_survived, self.top10s,
                self.vehicle_destroys, self.walk_distance, self.weapons_acquired,
                self.weekly_wins, self.wins)

    def __str__(self):
        return self.__repr__()


class RankedStats(BaseModel):
    """ Ranked Game Mode stats objects contain a player's aggregated
     ranked stats for a game mode in the context of a season.

    Attributes
    ----------
    current : Rank
        Player's current rank
    best : Rank
        Player's best rank
    assists : int
        Number of enemy players this player damaged that were killed by teammates
    avg_rank : float
        Average rank
    dbnos : int
        Number of enemy players knocked
    deaths : int
        Number of player deaths
    damage_dealt : float
        Total damage dealt. Note: Self inflicted damage is subtracted
    kda : float
        Kill death assist ratio
    kills : int
        Number of enemy players killed
    rounds_played : int
        Number of matches played
    top10_ratio : float
        Ratio of number of times this player made it to the top 10 in a match / times didn't make it to top 10
    top10s : int
        Number of times this player made it to the top 10 in a match
    win_ratio : float
        Ratio of number of matches won / matches didn't win
    wins : int
        Number of matches won
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.data = data

        self.current = Rank(tier=data.get("currentTier", {}), point=data.get("currentRankPoint"))
        self.best = Rank(tier=data.get("bestTier", {}), point=data.get("bestRankPoint"))

        self.assists: int = data.get("assists", 0)
        self.avg_rank: float = data.get("avgRank", 0.0)
        self.dbnos: int = data.get("dBNOs", 0)
        self.deaths: int = data.get("deaths", 0)
        self.damage_dealt: float = data.get("damageDealt", 0.0)
        self.kda: float = data.get("kda", 0.0)
        self.kills: int = data.get("kills", 0)
        self.rounds_played: int = data.get("roundsPlayed", 0)
        self.top10_ratio: float = data.get("top10Ratio", 0.0)
        self.top10s = int(self.rounds_played * self.top10_ratio)
        self.win_ratio: float = data.get("winRatio", 0.0)
        self.wins: int = data.get("wins", 0)

    def __repr__(self):
        return "RankedStats(assists={} avg_rank={} dbnos={} deaths={} damage_dealt={} kda={} kills={} " \
               "rounds_played={} top10_ratio={} top10s={} win_ratio={} wins={})".format(
                self.assists, self.avg_rank, self.dbnos, self.deaths, self.damage_dealt, self.kda, self.kills,
                self.rounds_played, self.top10_ratio, self.top10s, self.win_ratio, self.wins)

    def __str__(self):
        return self.__repr__()


class Rank:
    """ Scores earned in competition are included.

    Attributes
    ----------
    tier : str
        Return the competition tier.
    subtier : str
        Return the competition sub tier.
    point : int
        Returns the competition score.
    """
    def __init__(self, tier: dict, point):
        self.tier: str = tier.get("tier")
        self.subtier: str = tier.get("subTier")
        self.point: int = point

    def __eq__(self, other):
        return self.point == other.point

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.point < other.point

    def __gt__(self, other):
        return self.point > other.point

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __repr__(self):
        return "Rank(tier='{}' subtier='{}' point={})".format(self.tier, self.subtier, self.point)

    def __str__(self):
        if self.tier == "Unranked" or self.tier == "Master":
            return self.tier
        return "{} {}".format(self.tier, self.subtier)


class GameModeReceive(BaseModel):
    """ If the information varies depending on the game mode, check it through the appropriate class.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    type_class : class
        Type of data recalled
    solo : type_class
        Solo Play Stats
    solo_fpp : type_class
        Solo(First person) Play Stats
    duo : type_class, optional
        Duo Play Stats
    duo_fpp : type_class, optional
        Duo(First person) Play Stats
    squad : type_class
        Squad Play Stats
    squad_fpp : type_class
        Squad(First person) Play Stats
    """
    def __init__(self, data, type_class: Union[RankedStats, SeasonStats]):
        super().__init__(data)
        self.type_class = type_class

        self.solo = self.type_class(data=data.get('solo', {}))
        self.solo_fpp = self.type_class(data=data.get('solo-fpp', {}))
        self.squad = self.type_class(data=data.get('squad', {}))
        self.squad_fpp = self.type_class(data=data.get('squad-fpp', {}))
        if self.type_class == SeasonStats:
            self.duo = SeasonStats(data=data.get('duo', {}))
            self.duo_fpp = SeasonStats(data=data.get('duo-fpp', {}))
        else:
            self.duo = None
            self.duo_fpp = None

    def __repr__(self):
        return "GameModeReceive(type='{}')".format(self.type_class.__name__)

    def __str__(self):
        return self.__repr__()


class Stats(BaseModel):
    """ Total information returned by the player.
    Currently, it can only be checked through :Attributes:`Player.stats` imported from the leaderboard.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    average_damage : int
        Average Damage Amount
    average_rank : float
        Average rank point
    rounds_played : int
        Number of plays made
    tier : Tier
        Player's rank
    kda : float
        Kill and assist combined divided by death count.
    kills : int
        Kill Count
    wins : int
        Win Count
    """
    def __init__(self, data):
        super().__init__(data)
        if data is not None:
            self.data = data
            self.average_damage: int = data.get("averageDamage", 0)
            self.average_rank: float = data.get("averageRank", 0.0)
            self.rounds_played: int = data.get("games", 0)
            self.tier = Rank(tier=data, point=data.get("rankPoints"))
            self.kda: float = data.get("kda", 0.0)
            self.kills: int = data.get("kills", 0)
            self.wins: int = data.get("wins", 0)

    def __repr__(self):
        return "Stats(average_damage={} average_rank={} rounds_played={} tier={} kda={} kills={} " \
               "wins={})".format(self.average_damage, self.average_rank, self.rounds_played, self.rounds_played,
                                 self.tier, self.kda, self.kills, self.wins)

    def __str__(self):
        return self.__repr__()
