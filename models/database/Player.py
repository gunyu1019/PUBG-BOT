from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base

from module.pubgpy import Platforms

base = declarative_base()


class Player(base):
    __tablename__ = "player"

    name = Column(String(51))
    account_id = Column(String(41), primary_key=True)
    platform = Column(Enum(Platforms))
