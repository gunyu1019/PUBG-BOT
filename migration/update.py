import datetime
from typing import NamedTuple


class Update(NamedTuple):
    matches: datetime.datetime
    normal: datetime.datetime
    ranked: datetime.datetime
