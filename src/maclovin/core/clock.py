"""Clock and temporal window utilities for maclovin."""

from datetime import datetime, timezone, timedelta, date
from typing import Tuple, Optional
import zoneinfo
import email.utils


def get_timezone(tz_name: str) -> zoneinfo.ZoneInfo:
    """Carrega o fuso horário configurado com fallback seguro para UTC."""
    try:
        return zoneinfo.ZoneInfo(tz_name)
    except Exception:
        return zoneinfo.ZoneInfo("UTC")


def get_yesterday_window(
    tz_name: str = "America/Sao_Paulo",
    anchor_now: Optional[datetime] = None,
) -> Tuple[datetime, datetime, date]:
    """
    Calcula a janela exata de D-1 (00:00:00 até 23:59:59) no timezone configurado,
    convertida para UTC.
    
    Retorna: (start_utc, end_utc, target_date)
    """
    tz = get_timezone(tz_name)
    if anchor_now is None:
        now_local = datetime.now(tz)
    else:
        now_local = anchor_now.astimezone(tz) if anchor_now.tzinfo else anchor_now.replace(tzinfo=tz)

    target_date = (now_local - timedelta(days=1)).date()

    start_local = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        0,
        0,
        0,
        tzinfo=tz,
    )
    end_local = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        23,
        59,
        59,
        tzinfo=tz,
    )

    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    return start_utc, end_utc, target_date


def is_within_window(
    dt_utc: datetime,
    start_utc: datetime,
    end_utc: datetime,
) -> bool:
    """Verifica se o timestamp fornecido está contido no intervalo fechado de D-1."""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt_utc.astimezone(timezone.utc)

    return start_utc <= dt_utc <= end_utc


def parse_iso_or_rfc_date(date_str: str) -> Optional[datetime]:
    """
    Converte datas em formatos variados (RFC 822/2822 de RSS, ISO 8601 de Atom/APIs)
    para datetime em UTC.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # Tenta parsing RFC 2822 (padrão de feeds RSS)
    try:
        parsed_tuple = email.utils.parsedate_to_datetime(date_str)
        if parsed_tuple:
            if parsed_tuple.tzinfo is None:
                return parsed_tuple.replace(tzinfo=timezone.utc)
            return parsed_tuple.astimezone(timezone.utc)
    except Exception:
        pass

    # Tenta parsing ISO 8601
    try:
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    return None
