import json
import urllib.parse
import pathlib
from datetime import datetime, timezone
from maclovin.reporting.markdown_parser import extract_briefing_from_markdown
from maclovin.storage.supabase_client import get_briefing_from_supabase, save_briefing_to_supabase


def app(environ, start_response):
    query_str = environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_str)
    target_date_str = params.get("date", [None])[0]

    # 1. Tentar buscar direto do banco de dados permanente Supabase
    supabase_data = None
    try:
        supabase_data = get_briefing_from_supabase(target_date_str)
    except Exception as e:
        print(f"[API] Erro ao consultar Supabase: {e}")

    if supabase_data:
        body = json.dumps(supabase_data, ensure_ascii=False).encode("utf-8")
        status = "200 OK"
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]

    # 2. Fallback estático em JSON
    if target_date_str:
        specific_json = pathlib.Path(f"public/data/briefings/{target_date_str}.json")
        if specific_json.exists():
            payload = json.loads(specific_json.read_text(encoding="utf-8"))
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            status = "200 OK"
            headers = [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Access-Control-Allow-Origin", "*"),
                ("Content-Length", str(len(body))),
            ]
            start_response(status, headers)
            return [body]

    # 3. Fallback Markdown
    briefings_dir = pathlib.Path("briefings")
    selected_file = None

    if briefings_dir.exists():
        files = sorted(list(briefings_dir.glob("*.md")), reverse=True)
        if target_date_str:
            for f in files:
                if f.stem == target_date_str:
                    selected_file = f
                    break
        elif files:
            selected_file = files[0]

    if selected_file and selected_file.exists():
        payload = extract_briefing_from_markdown(selected_file)
        try:
            save_briefing_to_supabase(payload)
        except Exception:
            pass
    else:
        json_file = pathlib.Path("public/data/briefing.json")
        if json_file.exists():
            payload = json.loads(json_file.read_text(encoding="utf-8"))
        else:
            payload = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "total_items": 0,
                "tools": [],
                "opportunities": [],
                "business": [],
                "learning": [],
                "geek": [],
                "news": [],
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
