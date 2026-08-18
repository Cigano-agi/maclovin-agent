import json
from datetime import datetime
from maclovin.storage.supabase_client import get_all_dates_from_supabase


def app(environ, start_response):
    dates = []
    db_status = "ONLINE"
    try:
        dates = get_all_dates_from_supabase()
    except Exception as e:
        db_status = f"DEGRADED ({e})"

    payload = {
        "status": "ONLINE",
        "database": "Supabase PostgreSQL Cloud",
        "database_status": db_status,
        "total_editions_archived": len(dates),
        "latest_edition": dates[0] if dates else None,
        "platform": "Vercel Serverless Production",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    status = "200 OK"
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]
