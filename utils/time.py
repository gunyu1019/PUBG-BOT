"""GNU GENERAL PUBLIC LICENSE

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

from datetime import datetime


def get_time_to_string(playtime: datetime) -> str:
    if playtime.month <= 1:
        if playtime.day <= 1:
            if playtime.hour <= 0:
                if playtime.minute <= 0:
                    return f"{playtime.second}초"
                return f"{playtime.minute}분 {playtime.second}초"
            return f"{playtime.hour}시간 {playtime.minute}분 {playtime.second}초"
        return f"{playtime.day - 1}일 {playtime.hour}시간 {playtime.minute}분 {playtime.second}초"
    return f"{playtime.month - 1}달 {playtime.day - 1}일 {playtime.hour}시간 {playtime.minute}분 {playtime.second})"
