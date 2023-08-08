import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config.log_config import log
from models.database import *
from utils.database_config import database

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))

    log.info("Start PUBG BOT's Setup")

    # Database
    engine = create_engine(
        "mysql+pymysql://{username}:{password}@{host}:{port}/{database}".format(
            **database
        )
    )
    with Session(engine) as session:
        for table in [
            CurrentSeasonInfo,
            FavoritePlayer,
            MatchesPlayer,
            NormalStats,
            OnlinePlayer,
            Player,
            RankedStats
        ]:
            table.__base__.metadata.create_all(session.bind)
        session.commit()
    engine.dispose()

