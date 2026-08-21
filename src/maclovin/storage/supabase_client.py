"""Supabase client for persisting daily briefings, news items, and historical archives."""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rvoyllttmlluhwenhyln.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def _get_headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }


def save_briefing_to_supabase(briefing_data: Dict[str, Any]) -> bool:
    """Salva ou atualiza um briefing diário completo no Supabase PostgreSQL."""
    date_str = briefing_data.get("date")
    if not date_str:
        return False

    url = f"{SUPABASE_URL}/rest/v1/maclovin_briefings"
    payload = {
        "id": date_str,
        "reference_date": date_str,
        "data": briefing_data,
        "total_items": briefing_data.get("total_items", 0),
        "updated_at": "now()",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=_get_headers(),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[Supabase] Erro ao salvar briefing {date_str}: {e}")
        return False


def get_briefing_from_supabase(date_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Busca o briefing de uma data específica ou o mais recente no Supabase."""
    try:
        if date_str:
            url = f"{SUPABASE_URL}/rest/v1/maclovin_briefings?id=eq.{urllib.parse.quote(date_str)}&select=data"
        else:
            url = f"{SUPABASE_URL}/rest/v1/maclovin_briefings?order=reference_date.desc&limit=1&select=data"

        req = urllib.request.Request(
            url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                return data[0].get("data")
    except Exception as e:
        print(f"[Supabase] Erro ao buscar briefing: {e}")
    return None


def get_all_dates_from_supabase() -> List[str]:
    """Retorna todas as datas registradas em ordem decrescente."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/maclovin_briefings?order=reference_date.desc&select=id"
        req = urllib.request.Request(
            url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [row["id"] for row in data if "id" in row]
    except Exception as e:
        print(f"[Supabase] Erro ao buscar lista de datas: {e}")
    return []


def save_news_items_to_supabase(items: List[Dict[str, Any]], ref_date: str) -> bool:
    """Salva itens individuais no banco para busca analítica."""
    if not items:
        return True

    url = f"{SUPABASE_URL}/rest/v1/maclovin_news_items"
    rows = []
    for it in items:
        rows.append({
            "id": it.get("id"),
            "reference_date": ref_date,
            "source_id": it.get("source_id"),
            "title": it.get("title"),
            "canonical_url": it.get("canonical_url"),
            "published_date_utc": it.get("published_date_utc"),
            "summary": it.get("summary"),
            "why_it_matters": it.get("why_it_matters"),
            "pricing_model": it.get("pricing_model"),
            "item_type": it.get("item_type"),
            "tool_subtype": it.get("tool_subtype"),
            "key_features": it.get("key_features", []),
        })

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(rows).encode("utf-8"),
            headers=_get_headers(),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"[Supabase] Erro ao salvar news_items: {e}")
        return False
