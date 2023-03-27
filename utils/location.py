"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (c) 2021 gunyu1019

PUBG BOT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PUBG BOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PUBG BOT.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

from config.config import get_config
from utils.directory import directory


languages = {}
comment_files = os.listdir(os.path.join(directory, "config", "comment"))
for lng in comment_files:
    lng_file_without_ini = lng.strip(".ini")
    languages[lng_file_without_ini.lstrip("language_")] = get_config(
        lng_file_without_ini, path=["comment"]
    )


def comment(command_group: str, comment_id: str, language: str):
    if language not in languages.keys():
        language = "ko"
    parser = languages[language]
    return parser.get(command_group, comment_id).replace("\\n", "\n")
