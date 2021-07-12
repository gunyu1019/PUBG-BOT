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


from .enums import Platforms
from .models import PUBGModel


def get_season(d_season: int, platform: Platforms):
    """Randomly creates a season class. It's easier to look up specific season information without additional phrases.

    Parameters
    ----------
    d_season : int
        Any value for the season
    platform : Platforms
        Platform information for the season

    Returns
    -------
    Season :
        Contains classes for Season.
    """
    if platform == Platforms.STEAM or platform == Platforms.KAKAO:
        f_season = "pc"
    elif platform == Platforms.XBOX or platform == Platforms.PLAYSTATION or platform == Platforms.STADIA:
        f_season = "console"
    else:
        raise TypeError(
            "Platform information not found. PUBGpy only supports Steam, Kakao, XBOX, PlayStation, and Stadia.")

    if isinstance(d_season, int):
        d_season = str(d_season)
    d_season = d_season.zfill(2)

    return Season({
        "id": "division.bro.official.{}-2018-{}".format(f_season, d_season),
        "type": "season"
    })


class Season(PUBGModel):
    """Season objects each contain the ID of a season, which can be used to lookup season information for a player.

    Attributes
    ----------
    data : dict
        Source of Returned Original Data
    id : str
        A randomly generated ID assigned to this resource object for linking elsewhere in the season response
    type : str
        Identifier for this object type
    current : bool
        Indicates if the season is active
    off_season : bool
        Indicates if the season is not active
    """
    def __init__(self, data: dict):
        self.data = data

        self.type = self.data.get("type")
        self.id = self.data.get("id", "season")
        super().__init__(self)

        self.current = self.data.get("attributes", {}).get("isCurrentSeason")
        self.off_season = self.data.get("attributes", {}).get("isOffseason")

    def __repr__(self):
        return "Season(id='{}', current='{}', type='{}')".format(self.id, self.current, self.type)

    def __str__(self):
        return self.id
