import os
from datetime import datetime
from zoneinfo import ZoneInfo
from random import randint

def get_random_number(min_val: int = 0, max_val: int = 10) -> int:
    """Returns a random integer between min_val and max_val (inclusive)."""
    return randint(min_val, max_val)


def get_current_datetime():
    """Get current date, time and timezone in India."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    return {
        "date": now.strftime("%d %B %Y"),
        "day": now.strftime("%A"),
        "time": now.strftime("%I:%M:%S %p"),
        "timezone": "Asia/Kolkata",
        "iso_format": now.isoformat()
    }


def get_current_date():
    """Get today's date."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%d %B %Y")


def get_current_time():
    """Get current time."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%I:%M:%S %p")
