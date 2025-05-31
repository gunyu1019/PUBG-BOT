from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

base = declarative_base()


class MatchesPlayer(base):
    __tablename__ = "matches_player"

    account_id_with_match_id = Column(String(80), primary_key=True)
    account_id = Column(String(42))
    match_id = Column(String(62))
    match_index = Column(Integer)
    last_update = Column(DateTime)
