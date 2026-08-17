"""Vercel Serverless Function for /api/briefing."""

import http.server
import json
import urllib.parse
import pathlib
import re
from datetime import datetime, timezone


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

            item = {
                "id": f"{current_section}-{len(tools)+len(news)+len(learning)+len(geek)+1}",
                "source_id": source_id,
                "title": title,
                "canonical_url": url,
                "published_date_utc": f"{ref_date}T12:00:00Z",
                "summary": summary or title,
                "why_it_matters": why,
                "pricing_model": pricing,
                "item_type": "tool" if current_section == "tools" else ("learning" if current_section == "learning" else ("geek" if current_section == "geek" else "news")),
                "key_features": features,
            }

            if current_section == "tools":
                tools.append(item)
            elif current_section == "learning":
                learning.append(item)
            elif current_section == "geek":
                geek.append(item)
            elif current_section == "news":
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


class handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        target_date_str = query.get("date", [None])[0]

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
            # Fallback para data estática pré-renderizada
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

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
