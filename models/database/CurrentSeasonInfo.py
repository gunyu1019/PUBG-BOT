from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base

from module.pubgpy import Platforms

base = declarative_base()


class CurrentSeasonInfo(base):
    __tablename__ = "current_season_info"

    platform = Column(Enum(Platforms), primary_key=True)
    season = Column(String)
    last_update = Column(Date)
