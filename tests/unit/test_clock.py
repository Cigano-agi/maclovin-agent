import pytest
from datetime import datetime, timezone, date
import zoneinfo

from maclovin.core.clock import get_yesterday_window, is_within_window, parse_iso_or_rfc_date


def test_get_yesterday_window_sao_paulo():
    # Freeze anchor date to 2026-08-17 in Sao Paulo
    tz_name = "America/Sao_Paulo"
    tz = zoneinfo.ZoneInfo(tz_name)
    now = datetime(2026, 8, 17, 10, 0, 0, tzinfo=tz)

    start_utc, end_utc, target_date = get_yesterday_window(tz_name, anchor_now=now)

    assert target_date == date(2026, 8, 16)
    
    # In Sao Paulo (UTC-3), 2026-08-16 00:00:00 is 2026-08-16 03:00:00 UTC
    # and 2026-08-16 23:59:59 is 2026-08-17 02:59:59 UTC
    assert start_utc.year == 2026
    assert start_utc.month == 8
    assert start_utc.day == 16
    assert start_utc.hour == 3
    assert start_utc.minute == 0

    assert end_utc.year == 2026
    assert end_utc.month == 8
    assert end_utc.day == 17
    assert end_utc.hour == 2
    assert end_utc.minute == 59


def test_is_within_window():
    start_utc = datetime(2026, 8, 16, 3, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 8, 17, 2, 59, 59, tzinfo=timezone.utc)

    valid_dt = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    too_early = datetime(2026, 8, 16, 2, 59, 59, tzinfo=timezone.utc)
    too_late = datetime(2026, 8, 17, 3, 0, 1, tzinfo=timezone.utc)

    assert is_within_window(valid_dt, start_utc, end_utc) is True
    assert is_within_window(too_early, start_utc, end_utc) is False
    assert is_within_window(too_late, start_utc, end_utc) is False


def test_parse_iso_or_rfc_date():
    rfc_str = "Sun, 16 Aug 2026 14:30:00 +0000"
    dt = parse_iso_or_rfc_date(rfc_str)
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 16
    assert dt.hour == 14
    assert dt.tzinfo is not None

    iso_str = "2026-08-16T14:30:00Z"
    dt_iso = parse_iso_or_rfc_date(iso_str)
    assert dt_iso is not None
    assert dt_iso.year == 2026
    assert dt_iso.month == 8
    assert dt_iso.day == 16
