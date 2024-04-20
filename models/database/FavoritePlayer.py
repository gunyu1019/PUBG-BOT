from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import declarative_base

base = declarative_base()


class FavoritePlayer(base):
    __tablename__ = "favorite_player"

    idx = Column(Integer, primary_key=True)
    player_id = Column(String(41))
    discord_id = Column(String(41))


