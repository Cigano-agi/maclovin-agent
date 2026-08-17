"""Vercel Serverless API Handler for Maclovin Intelligence Dashboard."""

import http.server
import json
import urllib.parse
import pathlib
import os
import re
from datetime import datetime, timezone


def extract_briefing_from_markdown(file_path: pathlib.Path) -> dict:
    """Extrai itens e categorias a partir do arquivo Markdown salvo."""
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

            # Parse sublinhas
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
    """Vercel Serverless Python Handler."""

    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API Briefing
        if "/api/briefing" in path:
            briefings_dir = pathlib.Path("briefings")
            target_date_str = query.get("date", [None])[0]

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
                payload = {
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "total_items": 0,
                    "tools": [],
                    "learning": [],
                    "geek": [],
                    "news": [],
                    "latest_execution": {"status": "SUCCESS", "reference_date": "Hoje"},
                }

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API History
        elif "/api/history" in path:
            briefings_dir = pathlib.Path("briefings")
            dates = []
            if briefings_dir.exists():
                for f in sorted(list(briefings_dir.glob("*.md")), reverse=True):
                    dates.append(f.stem)
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"dates": dates}).encode("utf-8"))
            return

        # 3. API Status
        elif "/api/status" in path:
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"status": "SUCCESS", "version": "1.0", "platform": "Vercel Serverless"}).encode("utf-8"))
            return

        self._set_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"404 Not Found")
