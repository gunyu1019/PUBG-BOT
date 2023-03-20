

def time_to_string(time: float) -> str:
    play_time = str()
    play_time_hours = time // 3600
    play_time_minutes = time % 3600 // 60
    play_time_seconds = time % 3600 % 60
    if play_time_hours != 0:
        play_time += "{}시간".format(int(play_time_hours))
    if play_time_hours != 0 or play_time_minutes != 0:
        play_time += "{}분".format(int(play_time_minutes))
    play_time += "{}초".format(int(play_time_seconds))
    return play_time