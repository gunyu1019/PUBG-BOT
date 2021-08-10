import pymysql
import logging
import json

from datetime import datetime
from typing import Union

from utils.database import get_database

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


def get_date(date: dict):
    return datetime(
        year=date["years"],
        month=date["months"],
        day=date["days"],
        hour=date["hours"],
        minute=date["minutes"]
    )


def dump_data(data: Union[dict, list]):
    return json.dumps(data, indent=4)


def load_data(data: str):
    return json.loads(data)


if __name__ == "__main__":
    log.info("Start Migration Database")
    connect = get_database()
    cursor = connect.cursor(pymysql.cursors.DictCursor)
    command1 = pymysql.escape_string("DELETE FROM PUBG_BOT.player_data")
    command2 = pymysql.escape_string("DELETE FROM PUBG_BOT.season_stats")
    command3 = pymysql.escape_string("DELETE FROM PUBG_BOT.ranked_stats")
    cursor.execute(command1)
    cursor.execute(command2)
    cursor.execute(command3)

    log.info("Starting Convent Player Data")
    command = pymysql.escape_string("SELECT id, name, last_update, platform FROM PUBG_BOT.player")
    cursor.execute(command)

    data = cursor.fetchall()
    player_data = []
    duplicate_check = []
    for player in data:
        player_id = player.get("id")
        player_name = player.get("name")
        platform = player.get("platform")
        last_update: dict = load_data(player.get("last_update"))
        if player_id in duplicate_check:
            continue
        duplicate_check.append(player_id)

        # Not Need Date data
        last_update.pop("weapon")
        last_update.pop("matches")

        # Need Date data
        season = get_date(last_update.pop("normal"))
        ranked = get_date(last_update.pop("ranked"))

        command = pymysql.escape_string("SELECT html FROM PUBG_BOT.MATCHES_STATUS WHERE id=%s")
        cursor.execute(command, player_id)
        matches_data = cursor.fetchone()
        final_matches_data = []
        if matches_data is not None and matches_data != {}:
            _data = load_data(matches_data.get("html", "{}"))
            matches = _data.get("data", [{}])[0].get("relationships", {}).get("matches", {}).get("data", [])
            for match in matches:
                _match = match.get("id")
                final_matches_data.append(_match)

        player_data.append(
            (
                player_id,
                player_name,
                season.strftime("%Y-%m-%d %H:%M:%S"),
                ranked.strftime("%Y-%m-%d %H:%M:%S"),
                platform,
                dump_data(final_matches_data),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    command = pymysql.escape_string(
        "INSERT INTO PUBG_BOT.player_data("
        "player_id, nickname, season_date, ranked_date, platform, matches_data, matches_date"
        ") VALUES(%s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.executemany(command, player_data)
    log.info("Finish Convert Player Data")
    log.info("Starting Convert Normal Stats Data")
    command = pymysql.escape_string("SELECT id, html, season FROM PUBG_BOT.NORMAL_STATUS")
    cursor.execute(command)

    data = cursor.fetchall()
    season_data = []
    duplicate_check = []
    for status in data:
        player_id = status.get("id")
        html = load_data(status.get("html", "{}"))
        season = status.get("season")
        if player_id in duplicate_check:
            continue
        duplicate_check.append(player_id)

        convert_data = html.get("data", {}).get("attributes", {}).get("gameModeStats", {})
        season_data.append(
            (player_id, dump_data(convert_data), season)
        )
    command = pymysql.escape_string(
        "INSERT INTO PUBG_BOT.season_stats("
        "player_id, player_data, season"
        ") VALUES(%s, %s, %s)"
    )
    cursor.executemany(command, season_data)
    log.info("Finish Convert Normal Stats Data")
    log.info("Starting Convert Ranked Stats Data")
    command = pymysql.escape_string("SELECT id, html, season FROM PUBG_BOT.RANKED_STATUS")
    cursor.execute(command)

    data = cursor.fetchall()
    season_data = []
    duplicate_check = []
    for status in data:
        player_id = status.get("id")
        html = load_data(status.get("html", "{}"))
        season = status.get("season")
        if player_id in duplicate_check:
            continue
        duplicate_check.append(player_id)

        convert_data = html.get("data", {}).get("attributes", {}).get("rankedGameModeStats", {})
        season_data.append(
            (player_id, dump_data(convert_data), season)
        )
    command = pymysql.escape_string(
        "INSERT INTO PUBG_BOT.ranked_stats("
        "player_id, player_data, season"
        ") VALUES(%s, %s, %s)"
    )
    cursor.executemany(command, season_data)
    log.info("Finish Convert Ranked Stats Data")
    log.info("Finally Start Commit Data")
    connect.commit()
    connect.close()
