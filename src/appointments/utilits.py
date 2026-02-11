from datetime import datetime, date, time, timezone
import pytz
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_day_boundaries_in_utc(
        target_date: date,
        user_timezone: str = "Europe/Moscow"
) -> tuple[datetime, datetime]:
    user_tz = ZoneInfo(user_timezone)

    start_local = datetime.combine(target_date, time.min).replace(tzinfo=user_tz)
    end_local = datetime.combine(target_date, time.max).replace(tzinfo=user_tz)

    utc_tz = ZoneInfo("UTC")
    start_utc = start_local.astimezone(utc_tz)
    end_utc = end_local.astimezone(utc_tz)

    return start_utc, end_utc



def convert_time_to_utc(
        user_date: date,
        time_str: str,
        user_timezone: str
):
    hour, minute = map(int, time_str.split(":"))

    user_tz = pytz.timezone(zone=user_timezone)
    local_dt = datetime.combine(
        user_date,
        time(hour, minute)
    ).replace(tzinfo=user_tz)


    return local_dt.astimezone(timezone.utc)


def utc_to_local(utc_dt: datetime, user_timezone: str) -> datetime:
    return utc_dt.astimezone(ZoneInfo(user_timezone))