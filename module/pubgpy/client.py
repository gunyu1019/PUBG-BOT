"""
MIT License

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

import datetime
import logging

from .api import Api
from .player import Player
from .enums import Platforms, get_enum, Region, GameMode
from .errors import APIException
from .season import Season
from .matches import Matches
from .leaderboards import Leaderboards
from .tournaments import Tournaments
from .sample import Sample

log = logging.getLogger(__name__)


class Client:
    """Indicates the client connection to the PUBG.
     Save the platform type and token values through that class.

    Parameters
    ----------
    token : str
        Contains the token value issued by the PUBG API.
        If you have not been issued or if you forget, please get the key from https://developer.pubg.com/.
    platform : `str` or `Platforms`, optional
        `Platforms` information to report with API by substituting the value of `Platform` or string.
        Sometimes the platform type is not required for some features that do not require it.
    """
    def __init__(self, token: str, platform: (str, Platforms) = None):
        self.token = token
        if isinstance(platform, Platforms):
            self.Platform = platform.value
        else:
            self.Platform = platform
        self.requests = Api(token=token, platform=self.Platform)
        log.info("PUBGpy client was created. (Platform: {})".format(platform))

    def platform(self, platform: (str, Platforms) = None) -> (Platforms, str):
        """Change the platform type through the function.

        Parameters
        ----------
        platform : `str` or `Platforms`, optional
             Platforms information to report with API by substituting the value of `Platform` or string.
            Sometimes the platform type is not required for some features that do not require it.
            Default value is to initialize platform value.

        Returns
        -------
        Platforms :
            Returns platform value set.
        """
        log.info("PUBGpy changed platform ({} -> {})".format(self.platform, platform))
        if platform is None:
            self.Platform = platform

        return get_enum(Platforms, self.Platform)

    def player_id(self, player_id: str) -> Player:
        """Create a :class:`Player` arbitrarily.

        Notes
        -----
        Because it is created by randomly inserting a player's unique ID,
        things other than unique ID such as match information cannot be used.

        Parameters
        ----------
        player_id : str
            Contains user's unique ID value.

        Returns
        -------
        Player :
            Class of randomly inserted players is returned.
        """
        _data = {
            "id": player_id
        }
        return Player(client=self, data=_data)

    async def player(self, nickname: str):
        """Get a single player.

        Parameters
        ----------
        nickname : str
            Contains user's nickname

        Returns
        -------
        Player :
            Class containing the player's data is returned.
        """
        data = await self.players(players=[nickname])
        return data[0]

    async def players(self, players: list = None, ids: list = None):
        """Get a collection of up to 10 players.

        Parameters
        ----------
        players : list
            Contains elements to filter by name.
        ids : list
            Contains elements to filter by unique id.

        Returns
        -------
        Player :
            Data from various users retrieved is included in the class and returned.
        """
        path = "/players"
        if players is not None:
            join_data = "%2c".join(players)
            path += "?filter[playerNames]={}".format(join_data)
        if ids is not None:
            if players is not None:
                path += "&"
            else:
                path += "?"
            join_data = "%2c".join(ids)
            path += "filter[playerIds]={}".format(join_data)

        resp = await self.requests.get(path=path)
        data = resp.get('data')
        return [Player(client=self, data=_) for _ in data]

    async def current_season(self):
        """Get a current seasons.

        Returns
        -------
        Season :
            Returns current season value in progress.

        Raise
        -----
        ValueError :
            Raised when you can find current season.
        """
        seasons = await self.seasons()
        for i in seasons:
            if i.current:
                log.info("Current season value is {}.".format(i))
                return i
        log.error("Can not find current season.")
        raise ValueError("Can not find current season.")

    async def seasons(self):
        """Get the list of available seasons.

        Returns
        -------
        list :
            Returns season value that has been processed so far by adding it to `Season` class.
        """
        path = "/seasons"
        resp = await self.requests.get(path=path)
        data = resp.get('data')
        return [Season(_) for _ in data]

    async def season_stats(self, player_id: str, season: (Season, str) = None):
        """Get season information for a single player.

        Parameters
        ----------
        player_id : str
            Contains player's unique ID.
        season : `Season` or `str`
            Contains season class.

        Returns
        -------
        GameMode :
            Includes all information about general games by season according to game mode.
        """
        player = self.player_id(player_id=player_id)
        data = await player.season_stats(season)
        return data

    async def ranked_stats(self, player_id: str, season: (Season, str) = None):
        """Get ranked stats for a single player.

        Parameters
        ----------
        player_id : str
            Contains player's unique ID.
        season : `Season` or `str`
            Contains season class.

        Returns
        -------
        GameMode :
            Includes all information about ranked games by season according to game mode.
        """
        player = self.player_id(player_id=player_id)
        data = await player.ranked_stats(season)
        return data

    async def lifetime_stats(self, player_id: str):
        """Get lifetime stats for a single player.

        Parameters
        ----------
        player_id : str
            Contains player's unique ID.

        Returns
        -------
        GameMode :
            Includes all information about lifetime games by season according to game mode.
        """
        player = self.player_id(player_id=player_id)
        data = await player.lifetime_stats()
        return data

    async def weapon_mastery(self, player_id: str):
        """Get weapon mastery information for a single player

        Parameters
        ----------
        player_id : str
            Contains player's unique ID.

        Returns
        -------
        Weapon :
            Contains classes for Weapon mastery.
        """
        player = self.player_id(player_id=player_id)
        data = await player.weapon()
        return data

    async def survival_mastery(self, player_id: str):
        """Get survival mastery information for a single player

        Parameters
        ----------
        player_id : str
            Contains player's unique ID.

        Returns
        -------
        Survival :
            Contains classes for Survival mastery.
        """
        player = self.player_id(player_id=player_id)
        data = await player.survival()
        return data

    async def matches(self, match_id: str):
        """Get a single match.

        Notes
        -----
        Authorization is not required endpoint because it is not rate-limited.

        Parameters
        ----------
        match_id : str
            Contains match's unique ID.

        Returns
        -------
        Matches :
            Contains classes for Matches.
        """
        path = "/matches/{}".format(match_id)
        resp = await self.requests.get(path=path)
        data = resp.get('data')
        included = resp.get('included')
        return Matches(data=data, included=included)

    async def tournaments(self):
        """Get the list of available tournaments.

        Returns
        -------
        list :
            Contains a list of tournaments.
        """
        path = "/tournaments"
        resp = await self.requests.get(path=path, ni_shards=False)
        data = resp.get('data')
        return [Tournaments(self, x) for x in data]

    async def tournament_id(self, tournament_id: str):
        """Get information for a single tournament.

        Notes
        -----
        Match data values imported from a tournament can only be viewed through
         the match function contained in the tournament.

        Parameters
        ----------
        tournament_id : str
            Contains tournament's unique ID.

        Returns
        -------
        Tournaments :
            Contains classes for Tournaments.
        """
        path = "/tournaments/{}".format(tournament_id)
        resp = await self.requests.get(path=path, ni_shards=False)
        data = resp.get('data')
        return Tournaments(self, data)

    async def samples(self, create_at: (datetime.datetime, str) = None):
        """Get a list of sample matches.

        Parameters
        ----------
        create_at : datetime.datetime or str
            The starting search date in UTC.

        Returns
        -------
        Sample :
            Contains classes of sample.
        """
        path = "/samples"
        if create_at is not None:
            if isinstance(create_at, datetime.datetime):
                create_at = create_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            path += "?filter[createdAt-start]={}".format(create_at)
        resp = await self.requests.get(path=path)
        data = resp.get('data')
        return Sample(self, data)

    async def status(self):
        """Check the status of the API.

        Returns
        -------
        bool :
            Returns whether API is functioning normally.
        """
        path = "/status"
        try:
            await self.requests.get(path=path, ni_shards=False)
        except APIException:
            return False
        return True

    async def leaderboards(self, region: (str, Region), game_mode: (str, GameMode), season: (str, Season) = None):
        """Get the leaderboard for a game mode.

        Parameters
        ----------
        region : str or Region
            Contains Region information for the leaderboard you want to look up.
        game_mode : str or GameMode
            Contains Game Mode.
        season : str or Season
            Contains season class. If season is not included, bring up latest season information.

        Returns
        -------
        Leaderboards :
            Contains classes for Leaderboards.

        Raises
        ------
        TypeError :
            Unsupported platform (stadia not supported)
        """
        if season is None:
            season = await self.current_season()
        elif isinstance(season, Season):
            season = season.id

        if isinstance(game_mode, GameMode):
            game_mode = game_mode.value
        platform = self.requests.platform

        if platform == "steam" or "kakao":
            type_platform = "pc"
        elif platform == "xbox":
            type_platform = "xbox"
        elif platform == "psn":
            type_platform = "psn"
        else:
            raise TypeError("Unsupported platform (stadia not supported)")

        if isinstance(region, Region):
            region = region.value

        shard = '{}-{}'.format(type_platform, region)
        path = "/shards/{}/leaderboards/{}/{}".format(shard, season, game_mode)
        resp = await self.requests.get(path=path, ni_shards=False)

        data = resp.get('data')
        included = resp.get('included')
        return Leaderboards(self, data, included)
