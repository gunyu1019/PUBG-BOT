import datetime
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base

from module.pubgpy import SeasonStats as pubgNormalStats

base = declarative_base()


class NormalStats(base):
    __tablename__ = "normal_stats"

    account_id_with_session = Column(String, primary_key=True)
    account_id = Column(String)
    season = Column(String)
    update_time = Column(DateTime)
    deals = Column(Float, default=0.0)
    deaths = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    top10s = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    playtime = Column(Float, default=0.0)

    @classmethod
    def from_pubg(
            cls,
            player: str,
            season: str,
            stats: pubgNormalStats,
            update_time: datetime.datetime = datetime.datetime.now()
    ):
        account_id_with_session = "{}_{}".format(player, season)
        return cls(
            account_id_with_session=account_id_with_session,
            account_id=player,
            season=season,
            update_time=update_time,
            deals=stats.damage_dealt,
            deaths=stats.losses,
            kills=stats.kills,
            assists=stats.assists,
            top10s=stats.top10s,
            losses=stats.losses,
            played=stats.rounds_played,
            wins=stats.wins,
        )
