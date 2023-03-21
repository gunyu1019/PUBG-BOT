import datetime
import json
from typing import NamedTuple


class PlayerData(NamedTuple):
    player_id: str
    nickname: str
    season_date: datetime.datetime
    ranked_date: datetime.datetime
    platform: int
    matches_date: datetime.datetime
    matches_data: str

    @property
    def match_ids(self) -> list[str]:
        result = json.loads(self.matches_data)
        if isinstance(self.matches_data, dict):
            return []
        return result
