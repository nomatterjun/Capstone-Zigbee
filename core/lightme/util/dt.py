"""Datetime Utility for LightMe."""
from __future__ import annotations

import datetime
import zoneinfo

DATE_STR_FORMAT = "%Y-%m-%d"
UTC = datetime.timezone.utc
DEFAULT_TIME_ZONE: datetime.tzinfo = datetime.timezone.utc

def set_default_time_zone(time_zone: datetime.tzinfo) -> None:
    """Set default timezone to be used if not configured."""

    global DEFAULT_TIME_ZONE # pylint: disable=global-statement

    assert isinstance(time_zone, datetime.tzinfo)

    DEFAULT_TIME_ZONE = time_zone

def get_time_zone(time_zone_str: str) -> datetime.tzinfo | None:
    """Get timezone from string."""

    try:
        return zoneinfo.ZoneInfo(time_zone_str)
    except zoneinfo.ZoneInfoNotFoundError:
        return None

def utcnow() -> datetime.datetime:
    """Get now in UTC TimeZone."""

    return datetime.datetime.now(UTC)

def now(time_zone: datetime.tzinfo | None = None) -> datetime.datetime:
    """Get now of given timezone."""

    return datetime.datetime.now(time_zone or DEFAULT_TIME_ZONE)
