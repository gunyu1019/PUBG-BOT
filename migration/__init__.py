import datetime

import pymysql
import pymysql.cursors
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config.config import get_config
from config.log_config import log
from models import database as db
from module import pubgpy
from module.statsType import StatsPlayType

from migration.player_data import PlayerData
from migration.ranked_stats import RankedStats
from migration.season_stats import SeasonStats
from migration.update import Update

parser = get_config()


if __name__ == "__main__":
    log.info("Starting Migration from PUBG BOT to PUBG STATS.")
    log.info("Please do not stop! It can run only once.")
    database_section = parser.get("Default", "database")
    database_config = {
        "username": parser.get(database_section, "user"),
        "host": parser.get(database_section, "host"),
        "password": parser.get(database_section, "pass"),
        "database": parser.get(database_section, "database"),
        "port": parser.getint(database_section, "port", fallback=3306),
    }
    database = pymysql.connect(
        user=database_config["username"],
        host=database_config["host"],
        password=database_config["password"],
        database="PUBG_BOT",
        port=database_config["port"],
    )
    log.info("Connected at PUBG BOT Database.")
    cursor = database.cursor(pymysql.cursors.DictCursor)
    log.info("Searching in Player Data.")
    cursor.execute("SELECT * from player_data")
    player_data = [PlayerData(**x) for x in cursor.fetchall()]
    log.info("Found {} players in Player Data.".format(len(player_data)))

    log.info("Searching in Ranked Data.")
    cursor.execute("SELECT * from ranked_stats")
    ranked_stats = [RankedStats(**x) for x in cursor.fetchall()]
    log.info("Found {} data in Ranked Data.".format(len(ranked_stats)))

    log.info("Searching in Season Data.")
    cursor.execute("SELECT * from season_stats")
    normal_data = [SeasonStats(**x) for x in cursor.fetchall()]
    log.info("Found {} data in Season Data.".format(len(normal_data)))
    database.close()

    log.info("Connected at PUBG STATS Database.")
    engine = create_engine(
        "mysql+pymysql://{username}:{password}@{host}:{port}/{database}".format(
            **database_config
        )
    )
    with Session(engine) as session:
        _player_data = []
        _player_update_time = {}
        log.info("Found {} players.".format(len(player_data)))
        log.info("Starting Migration Player Data")
        _matches_data = []
        for player in player_data:
            _player = db.Player(
                name=player.nickname,
                account_id=player.player_id,
                platform=list(pubgpy.Platforms)[player.platform],
            )
            _player_update_time[player.player_id] = Update(
                **{
                    "matches": player.matches_date,
                    "ranked": player.ranked_date,
                    "normal": player.season_date,
                }
            )
            _player_data.append(_player)

            if len(player.match_ids) > 0:
                log.info(
                    "Found {} {}s's matches.".format(
                        len(player.match_ids), player.nickname
                    )
                )

            detect_duplication_matches = []
            for index, match_id in enumerate(player.match_ids):
                if match_id in detect_duplication_matches:
                    continue
                detect_duplication_matches.append(match_id)
                _matches_data.append(
                    db.MatchesPlayer(
                        **{
                            "account_id_with_match_id": "{}_{}".format(
                                player.player_id, match_id
                            ),
                            "account_id": player.player_id,
                            "match_id": match_id,
                            "match_index": index,
                            "last_update": getattr(
                                _player_update_time[player.player_id],
                                "matches",
                                datetime.datetime.now(),
                            ),
                        }
                    )
                )
            if len(detect_duplication_matches) > 0:
                log.info(
                    "Found {}'s {} duplication matches.".format(
                        player.nickname, len(detect_duplication_matches)
                    )
                )
        # session.add_all(_player_data)
        # session.commit()
        session.add_all(_matches_data)

        log.info("Starting Migration Season Data")
        _season_data = []
        detect_duplication_season = []
        for season in normal_data:
            data = pubgpy.GameModeReceive(season.data, type_class=pubgpy.SeasonStats)
            for fpp in [False, True]:
                for play_type in [
                    StatsPlayType.SOLO,
                    StatsPlayType.DUO,
                    StatsPlayType.SQUAD,
                ]:
                    _season = db.NormalStats().from_pubg(
                        player=season.player_id,
                        season=season.season,
                        play_type=play_type,
                        stats=getattr(
                            data, str(play_type.value) + ("" if not fpp else "_fpp")
                        ),
                        fpp=fpp,
                        update_time=getattr(
                            _player_update_time.get(season.player_id),
                            "normal",
                            datetime.datetime.now(),
                        ),
                    )
                    if _season.account_id_with_season in detect_duplication_season:
                        continue
                    detect_duplication_season.append(_season.account_id_with_season)
                    _season_data.append(_season)

        log.info("Starting Migration Ranked Data")
        # session.add_all(_season_data)
        _ranked_data = []
        detect_duplication_ranked = []
        for ranked in ranked_stats:
            data = pubgpy.GameModeReceive(ranked.data, type_class=pubgpy.RankedStats)
            for fpp in [False, True]:
                for play_type in [StatsPlayType.SOLO, StatsPlayType.SQUAD]:
                    _season = db.RankedStats().from_pubg(
                        player=ranked.player_id,
                        season=ranked.season,
                        play_type=play_type,
                        stats=getattr(
                            data, str(play_type.value) + ("" if not fpp else "_fpp")
                        ),
                        fpp=fpp,
                        update_time=getattr(
                            _player_update_time.get(ranked.player_id),
                            "ranked",
                            datetime.datetime.now(),
                        ),
                    )
                    if _season.account_id_with_season in detect_duplication_ranked:
                        continue
                    detect_duplication_ranked.append(_season.account_id_with_season)
                    _ranked_data.append(_season)
        # session.add_all(_ranked_data)
        log.info("Finished Migration")
        session.commit()
    engine.dispose()
