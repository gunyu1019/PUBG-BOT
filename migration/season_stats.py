import json
from typing import NamedTuple


class SeasonStats(NamedTuple):
    player_id: str
    player_data: str
    season: str

    @property
    def data(self) -> dict:
        return json.loads(self.player_data)
