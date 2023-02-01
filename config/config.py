import os

from typing import List
from configparser import ConfigParser
from utils.directory import directory


def get_config(name: str = "config", path: List[str] = None) -> ConfigParser:
    if path is None:
        path = []
    path.append("{0}.ini".format(name))

    parser = ConfigParser()
    parser.read(
        os.path.join(
            directory,
            "config",
            *path
        ),
        encoding="utf-8"
    )
    return parser
