from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import declarative_base
from datetime import datetime

base = declarative_base()


class OnlinePlayer(base):
    __tablename__ = "online_player"

    idx = Column(TINYINT, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    player = Column(Integer, default=0)
