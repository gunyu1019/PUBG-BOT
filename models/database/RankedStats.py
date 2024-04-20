import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base

from module.pubgpy import RankedStats as pubgRankedStats
from module.statsType import StatsPlayType

base = declarative_base()


class RankedStats(base):
    __tablename__ = "ranked_stats"

    account_id_with_season = Column(String(92), primary_key=True)
    account_id = Column(String(41))
    type = Column(Enum(StatsPlayType))
    fpp = Column(Boolean)
    season = Column(String(50))
    update_time = Column(DateTime)
    current_tier = Column(String(10), nullable=True)
    current_sub_tier = Column(String(2), nullable=True)
    current_point = Column(Integer, default=0)
    best_tier = Column(String(10), nullable=True)
    best_sub_tier = Column(String(2), nullable=True)
    best_point = Column(Integer, default=0)

    average_rank = Column(Float, default=0.0)
    deals = Column(Float, default=0.0)
    deaths = Column(Integer, default=0)
    dbnos = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    top10s = Column(Integer, default=0)
    kda_point = Column(Float, default=0.0)
    played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    win_point = Column(Float, default=0.0)

    @classmethod
    def from_pubg(
        cls,
        player: str,
        season: str,
        stats: pubgRankedStats,
        play_type: StatsPlayType,
        fpp: bool,
        update_time: datetime.datetime = datetime.datetime.now(),
    ):
        account_id_with_season = "{}_{}_{}{}".format(
            player, season, play_type.value, "_fpp" if fpp else ""
        )
        return cls(
            account_id_with_season=account_id_with_season,
            account_id=player,
            type=play_type,
            fpp=fpp,
            season=season,
            update_time=update_time,
            current_tier=stats.current.tier,
            current_sub_tier=stats.current.subtier,
            current_point=stats.current.point if stats.current.point is not None else 0,
            best_tier=stats.best.tier,
            best_sub_tier=stats.best.subtier,
            best_point=stats.best.point if stats.best.point is not None else 0,
            average_rank=stats.avg_rank,
            deals=stats.damage_dealt,
            dbnos=stats.dbnos,
            deaths=stats.deaths,
            kills=stats.kills,
            assists=stats.assists,
            top10s=stats.top10s,
            kda_point=stats.kda,
            played=stats.rounds_played,
            wins=stats.wins,
            win_point=stats.win_ratio,
        )
