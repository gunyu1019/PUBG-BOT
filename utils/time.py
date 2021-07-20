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
