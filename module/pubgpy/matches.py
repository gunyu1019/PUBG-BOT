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

from .models import BaseModel
from datetime import datetime
from .enums import MatchType, MapName, SeasonStats, get_enum, DeathType, GameMode, Platforms


class MatchesBaseModel(BaseModel):
    """Base model for match data."""
    def __init__(self, match_class):
        self.id: str = match_class.id
        self.type: str = match_class.type
        super().__init__(match_class.data)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        return self.id == other.id and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)


class Roster(MatchesBaseModel):
    """ Rosters track the scores of each opposing group of participants. Rosters can have one or many participants
     depending on the game mode. Roster objects are only meaningful within the context of a match and are not exposed
      as a standalone resource.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the matches response
    type : str
        Identifier for this object type
    shard : Platforms
        Type of shard ID
    rank : int
        Roster's placement in the match
    team_id : int
        An arbitrary ID assigned to this roster
    won : str
        Indicates if this roster won the match
    teams : list
        An array of references to participant objects that can be found in the included array
    """
    def __init__(self, data):
        self.data = data

        self.type: str = data.get("type", "roster")
        self.id: str = data.get("id")

        super().__init__(self)

#       attributes
        attributes = data.get("attributes", {})
        self.shard: Platforms = get_enum(Platforms, attributes.get("shardId"))
        self.rank: int = attributes.get("stats", {}).get("rank")
        self.team_id: int = attributes.get("stats", {}).get("teamId")
        self.won: str = attributes.get("won")

#       relationships
        self.relationships = data.get("relationships", {})
        self.teams = [x.get("id") for x in self.relationships.get("participants", {}).get("data", {})]

    def __repr__(self):
        return "Roster(id='{}' type='{}' shard='{}' rank={} team_id={} won='{}' teams='{}') ".format(
                self.id, self.type, self.shard, self.rank, self.team_id, self.won, self.teams)

    def __str__(self):
        return self.__repr__()


class Participant(MatchesBaseModel):
    """ Asset objects contain a URL string that links to a telemetry.json file, which will contain an array
     of event objects that provide further insight into a match.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the matches response
    type : str
        Identifier for this object type
    shard : Platforms
        Type of shard ID
    dbnos : int
        Number of players knocked
    assists : int
        Number of enemy players this player damaged that were killed by teammates
    boosts : int
        Number of boost items used
    damage_dealt : float
        Total damage dealt. Note: Self inflicted damage is subtracted
    death_type : DeathType
        The way by which this player died, or alive if they didn't
    headshot_kills : int
        Number of enemy players killed with headshots
    heals : int
        Number of healing items used
    kill_place : int
        This player's rank in the match based on kills
    kill_streaks : int
        Total number of kill streaks
    kills : int
        Number of enemy players killed
    longest_kill : float
        Highest Longest Kill
    name : str
        PUBG IGN of the player associated with this participant
    player_id : str
        Account ID of the player associated with this participant
    revives : int
        Number of times this player revived teammates
    ride_distance : float
        Total distance traveled in vehicles measured in meters
    road_kills : int
        Number of kills while in a vehicle
    swim_distance : float
        Total distance traveled while swimming measured in meters
    team_kills : int
        Number of times this player killed a teammate
    time_survived : float
        Amount of time survived measured in seconds
    vehicle_destroys : int
        Amount of Number of vehicles destroyed
    walk_distance : float
        Total distance traveled on foot measured in meters
    weapons_acquired : int
        Number of weapons picked up
    win_place : int
        This player's placement in the match
    """
    def __init__(self, data):
        self.data = data

        self.type: str = data.get("type", "participant")
        self.id: str = data.get("id")
        super().__init__(self)

#       attributes
        attributes = data.get("attributes", {})
        self.shard = get_enum(Platforms, attributes.get("shardId"))

#       attributes(stats)
        stats = attributes.get("stats", {})
        self.dbnos: int = stats.get("DBNOs", 0)
        self.assists: int = stats.get("assists", 0)
        self.boosts: int = stats.get("boosts", 0)
        self.damage_dealt: float = stats.get("damageDealt", 0.0)
        self.death_type: DeathType = get_enum(DeathType, stats.get("deathType"))
        self.headshot_kills: int = stats.get("headshotKills", 0)
        self.heals: int = stats.get("heals", 0)
        self.kill_place: int = stats.get("killPlace", 0)
        self.kill_streaks: int = stats.get("killStreaks", 0)
        self.kills: int = stats.get("kills", 0)
        self.longest_kill: float = stats.get("longestKill", 0.0)
        self.name: str = stats.get("name")
        self.player_id: str = stats.get("playerId")
        self.revives: int = stats.get("revives", 0)
        self.ride_distance: float = stats.get("rideDistance", 0.0)
        self.road_kills: int = stats.get("roadKills", 0)
        self.swim_distance: float = stats.get("swimDistance", 0.0)
        self.team_kills: int = stats.get("teamKills", 0)
        self.time_survived: float = stats.get("timeSurvived", 0.0)
        self.vehicle_destroys: int = stats.get("vehicleDestroys", 0)
        self.walk_distance: float = stats.get("walkDistance", 0.0)
        self.weapons_acquired: int = stats.get("weaponsAcquired", 0)
        self.win_place: int = stats.get("winPlace", 0)

    def __repr__(self):
        return "Participant(id='{}' type='{}' shard='{}' dbnos={} assists={} boosts={} damage_dealt={} " \
               "death_type='{}' headshot_kills={} heals={} kill_place={} kill_streaks={} kills={} " \
               "longest_kill={} name='{]' player_id='{}' revives={} ride_distance={} road_kills={} " \
               "swim_distance={} team_kills={} time_survived={} vehicle_destroys={} walk_distance={} " \
               "weapons_acquired={} win_place={})".format(
                self.id, self.type, self.shard, self.dbnos, self.assists, self.damage_dealt, self.death_type,
                self.headshot_kills, self.heals, self.kill_place, self.kill_streaks, self.kills, self.longest_kill,
                self.name, self.player_id, self.revives, self.ride_distance, self.road_kills, self.swim_distance,
                self.team_kills, self.time_survived, self.vehicle_destroys, self.walk_distance, self.weapons_acquired,
                self.win_place)

    def __str__(self):
        return self.name


class Assets(MatchesBaseModel):
    """ Asset objects contain a URL string that links to a telemetry.json file, which will contain an array
     of event objects that provide further insight into a match.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the matches response
    type : str
        Identifier for this object type
    shard : Platforms
        Type of shard ID
    url : str
        Link to the telemetry.json file
    created_at : str
        Time of telemetry creation
    name : str
        Telemetry
    """
    def __init__(self, data):
        self.data = data

        self.type = data.get("type", "participant")
        self.id = data.get("id")

        super().__init__(self)

#       attributes
        attributes = data.get("attributes", {})
        self.shard: Platforms = get_enum(Platforms, attributes.get("shardId"))
        self.url: str = attributes.get("url")
        created_at = attributes.get("createdAt")
        self.created_at: datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None)
        self.name: str = attributes.get("name", "Telemetry")

    def __repr__(self):
        return "Assets(id='{}' type='{}' shard='{}' url='{}' created_at='{}' name='{}') ".format(
                self.id, self.type, self.shard, self.url, self.created_at, self.name)

    def __str__(self):
        return self.__repr__()


class Matches(MatchesBaseModel):
    """ Match objects contain information about a completed match such as the game mode played, duration,
     and which players participated.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    included :
        Source data for additional players.
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the matches response
    type : str
        Identifier for this object type
    gamemode : GameMode
        Matches's game mode
    title : str
        Identifies the studio and game
    shard : Platforms
        Type of shard ID
    tags : str
        Type of tag (Sometimes Not Worked)
    map : MapName
        Map name
    match_type : MatchType
        Type of match
    duration : int
        Length of the match measured in seconds
    stats : str
        Type of stats (Sometimes Not Worked)
    state : SeasonStats
        State of the season
    created_at : datetime.datetime
        Time this match object was stored in the API
    custom : bool
        True if this match is a custom match
    rosters : list
        Contains ID values for Rosters.
    assets : list
        Contains ID values for Assets.
    participant : list of Participant
        A class containing user data is included.
    roster : list of Roster
        A class containing team data is included.
    asset : list of Asset
        A class containing asset data is included.
    """
    def __init__(self, data, included):
        self.data = data
        self.included = included

#       data Information (general)
        self.id: str = data.get("id")
        self.type: str = data.get("type", "matches")
        super().__init__(self)

#       data Information (attributes)
        attributes = data.get("attributes", {})
        self.gamemode: GameMode = get_enum(GameMode, attributes.get("gameMode"))
        self.title: str = attributes.get("titleId")
        self.shard: Platforms = get_enum(Platforms, attributes.get("shardId"))
        self.tags: str = attributes.get("tags")
        self.map: MapName = get_enum(MapName, attributes.get("mapName"))
        self.match_type: MatchType = get_enum(MatchType, attributes.get("matchType"))
        self.duration: int = attributes.get("duration")
        self.stats: str = attributes.get("stats")
        self.state: SeasonStats = get_enum(SeasonStats, attributes.get("seasonState"))

        created_at = attributes.get("createdAt")
        self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=None)
        self.custom = attributes.get("isCustomMatch")

#       data Information (relationships)
        relationships = data.get("relationships", {})
        self.rosters = [x.get("id") for x in relationships.get("rosters", {}).get("data", [])]
        self.assets = [x.get("id") for x in relationships.get("assets", {}).get("data", [])]
#       self.rounds = [x.get("id") for x in relationships.get("rounds", {}).get("data", [])]
#       self.spectators = [x.get("id") for x in relationships.get("spectators", {}).get("data", [])]

#       include Information
        self.participant = list()
        self.roster = list()
        self.asset = list()
        for i in self.included:
            if i.get("type") == "participant":
                self.participant.append(Participant(i))
            elif i.get("type") == "roster":
                self.roster.append(Roster(i))
            elif i.get("type") == "asset":
                self.asset.append(Assets(i))

    def __repr__(self):
        return "Matches(id='{}' type='{}' gamemode='{}' title='{}' shard='{}' tags='{}' map_name='{}' " \
               "match_type='{}' duration={} stats'{}' state='{}' created_at='{}' custom='{}') ".format(
                self.id, self.type, self.gamemode, self.title, self.shard, self.tags, self.map, self.match_type,
                self.duration, self.stats, self.state, self.created_at, self.custom)

    def __str__(self):
        return self.__repr__()

    def filter(self, filter_id, base_model: (Roster, Participant, Assets) = None):
        """
        Find class(Roster, Participant, Assets) for a specific ID.

        Parameters
        ----------
        filter_id : str
            Insert the ID value to find.
        base_model : class, optional
            Insert a class about what to find among Assets, Users(Participant), and Teams(Roster).
            If you don't put in a value, search among the total values.

        Returns
        -------
        Roster, Participant, Assets :
            Returns filtered class.

        Raises
        ------
        ValueError :
            No results for the item in searching data
        """
        list_search = list()
        if base_model is not None:
            if base_model == Roster:
                list_search = self.roster
            elif base_model == Participant:
                list_search = self.participant
            elif base_model == Assets:
                list_search = self.asset
        else:
            list_search.extend(self.roster)
            list_search.extend(self.participant)
            list_search.extend(self.asset)

        if filter_id in list_search or len(list_search) == 0:
            raise ValueError("No results for the item in searching data")

        result = None
        for x in list_search:
            if x.id == filter_id:
                result = x
        return result

    def get_player(self, nickname: str):
        """
        Recall users configured with nicknames from the list of players.

        Parameters
        ----------
        nickname : str
            Player's Nickname

        Returns
        -------
        Participant : optional
            If you find a suitable user for the nickname, the appropriate class(Participant) is returned.
        """
        players = self.participant
        for i in players:
            if i.name == nickname:
                return i

    def get_player_id(self, player_id: str):
        """
        Recall users configured with player's id from the list of players.

        Parameters
        ----------
        player_id : str
            Player's ID

        Returns
        -------
        Participant : optional
            If you find a suitable user for the nickname, the appropriate class(Participant) is returned.
        """
        players = self.participant
        for i in players:
            if i.player_id == player_id:
                return i

    def get_team(self, player_id: str):
        """
        Bring up a team through user ID.

        Parameters
        ----------
        player_id : str
            Player's ID

        Returns
        -------
        Roster : optional
            If a value exists, the Roster class is returned; if not, None is returned.
        """
        rosters = self.roster
        for team in rosters:
            for member in team.teams:
                if member == player_id:
                    return team
