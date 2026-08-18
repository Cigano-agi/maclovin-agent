import json
import pathlib
from maclovin.storage.supabase_client import get_all_dates_from_supabase


def app(environ, start_response):
    dates = []
    try:
        dates = get_all_dates_from_supabase()
    except Exception as e:
        print(f"Erro ao buscar datas do Supabase: {e}")

    if not dates:
        briefings_dir = pathlib.Path("briefings")
        if briefings_dir.exists():
            files = sorted(list(briefings_dir.glob("*.md")), reverse=True)
            dates = [f.stem for f in files]

    if not dates:
        history_json = pathlib.Path("public/data/history.json")
        if history_json.exists():
            try:
                payload = json.loads(history_json.read_text(encoding="utf-8"))
                dates = payload.get("dates", [])
            except Exception:
                pass

    body = json.dumps({"dates": dates}, ensure_ascii=False).encode("utf-8")
    status = "200 OK"
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]
