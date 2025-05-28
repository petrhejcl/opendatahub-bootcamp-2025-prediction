# presentation/utils.py
import datetime


def get_current_time():
    now = datetime.datetime.now()
    rounded_minute = 5 * round(now.minute / 5)

    if rounded_minute == 60:
        rounded_time = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0)

    return rounded_time
