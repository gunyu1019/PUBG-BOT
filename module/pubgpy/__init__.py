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

__title__ = 'PUBGpy'
__author__ = 'gunyu1019'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2021 gunyu1019'
__version__ = '1.0.0'

from .api import Api
from .client import Client
from .enums import *
from .errors import *
from .leaderboards import Leaderboards
from .mastery import Weapon, Survival, Medal, WeaponSummary, Stats
from .matches import Roster, Participant, Assets, Matches
from .player import Player, GameModeReceive, SeasonStats, RankedStats, Rank
from .sample import Sample
from .season import get_season, Season
from .tournaments import Tournaments
