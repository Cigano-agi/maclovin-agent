import json
import urllib.parse
import pathlib
import re
from datetime import datetime, timezone
from maclovin.intelligence.translator import translate_to_pt_br
from maclovin.ingestion.category_classifier import classify_category


def extract_briefing_from_markdown(file_path: pathlib.Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    ref_date = file_path.stem

    tools = []
    news = []
    learning = []
    geek = []

    current_section = None
    lines = content.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "## 🛠️ Radar de Ferramentas" in line:
            current_section = "tools"
        elif "## 📚 Aprender Tecnologia" in line:
            current_section = "learning"
        elif "## 🎮 Universo Geek" in line:
            current_section = "geek"
        elif "## 📰 Principais Notícias" in line:
            current_section = "news"
        elif line.startswith("## 📊"):
            current_section = None

        if current_section and line.startswith("### "):
            title = re.sub(r"^### \d+\.\s*", "", line)
            source_id = "feed"
            pricing = "Não especificado"
            summary = ""
            why = ""
            url = "#"

            j = i + 1
            features = []
            while j < len(lines) and not lines[j].strip().startswith("### ") and not lines[j].strip().startswith("## "):
                sub = lines[j].strip()
                if "**Fonte:**" in sub:
                    src_match = re.search(r"\*\*Fonte:\*\*\s*`([^`]+)`", sub)
                    if src_match:
                        source_id = src_match.group(1)
                    if "[GRÁTIS" in sub:
                        pricing = "Grátis / Open-Source"
                    elif "[FREEMIUM]" in sub:
                        pricing = "Freemium"
                    elif "[PAGO" in sub:
                        pricing = "Pago"
                elif sub.startswith("> **O que faz:**") or sub.startswith(">"):
                    summary = sub.replace("> **O que faz:**", "").replace(">", "").strip()
                elif "💡" in sub:
                    why = re.sub(r"^💡\s*(\*\*[^:]+:\*\*)?\s*", "", sub)
                elif sub.startswith("- ✔"):
                    features.append(sub.replace("- ✔", "").strip())
                elif "🔗 **Link" in sub:
                    url_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", sub)
                    if url_match:
                        url = url_match.group(2)
                j += 1

            translated_title = translate_to_pt_br(title)
            translated_summary = translate_to_pt_br(summary or title)
            translated_why = translate_to_pt_br(why) if why else "Acompanhamento relevante para inovação e desenvolvimento."

            # Determinar a categoria real do item usando o classificador estrito
            real_cat = classify_category(translated_title, translated_summary, current_section)

            item = {
                "id": f"{real_cat}-{len(tools)+len(news)+len(learning)+len(geek)+1}",
                "source_id": source_id,
                "title": translated_title,
                "canonical_url": url,
                "published_date_utc": f"{ref_date}T12:00:00Z",
                "summary": translated_summary,
                "why_it_matters": translated_why,
                "pricing_model": pricing,
                "item_type": "tool" if real_cat == "tools" else real_cat,
                "key_features": [translate_to_pt_br(f) for f in features],
            }

            if real_cat == "tools":
                tools.append(item)
            elif real_cat == "learning":
                learning.append(item)
            elif real_cat == "geek":
                geek.append(item)
            else:
                news.append(item)

        i += 1

    return {
        "date": ref_date,
        "total_items": len(tools) + len(news) + len(learning) + len(geek),
        "tools": tools,
        "learning": learning,
        "geek": geek,
        "news": news,
        "latest_execution": {
            "reference_date": ref_date,
            "status": "SUCCESS",
            "items_collected_count": len(tools) + len(news) + len(learning) + len(geek),
        },
    }


def app(environ, start_response):
    query_str = environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_str)
    target_date_str = params.get("date", [None])[0]

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
    else:
        json_file = pathlib.Path("public/data/briefing.json")
        if json_file.exists():
            payload = json.loads(json_file.read_text(encoding="utf-8"))
        else:
            payload = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "total_items": 0,
                "tools": [],
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
