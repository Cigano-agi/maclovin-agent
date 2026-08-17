"""Vercel Serverless Function for live synchronization (POST /api/run)."""

import http.server
import json
import urllib.parse
from datetime import datetime, timezone

from maclovin.config import load_config
from maclovin.core.pipeline import Pipeline
from maclovin.intelligence.factory import create_llm_provider


class handler(http.server.BaseHTTPRequestHandler):
    """Manipulador Serverless para disparar sincronização ao vivo na Vercel."""

    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        try:
            cfg = load_config()
            provider = create_llm_provider(cfg.ai)
            # Na Vercel Serverless, executa o pipeline em modo memória (dry_run ou sem travar sqlite)
            pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=None)
            report = pipeline.run(dry_run=True)

            tools = [it.model_dump(mode="json") for it in report.tools_and_launches]
            news = [it.model_dump(mode="json") for it in report.standalone_news] + [
                {
                    "id": ev.id,
                    "source_id": ev.main_topic_id,
                    "title": ev.title,
                    "canonical_url": ev.news_items[0].canonical_url if ev.news_items else "#",
                    "published_date_utc": f"{report.reference_date.isoformat()}T12:00:00Z",
                    "summary": ev.consolidated_summary,
                    "why_it_matters": ev.why_it_matters,
                    "pricing_model": "Não especificado",
                    "item_type": "news",
                    "key_features": [],
                }
                for ev in report.events
            ]
            learning = [it.model_dump(mode="json") for it in report.learning_items]
            geek = [it.model_dump(mode="json") for it in report.geek_items]

            payload = {
                "status": "SUCCESS",
                "date": report.reference_date.isoformat(),
                "total_items": len(tools) + len(news) + len(learning) + len(geek),
                "tools": tools,
                "news": news,
                "learning": learning,
                "geek": geek,
                "latest_execution": {
                    "reference_date": report.reference_date.isoformat(),
                    "status": "SUCCESS",
                    "items_collected_count": len(tools) + len(news) + len(learning) + len(geek),
                },
            }

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self._set_headers(500, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8"))

    def do_GET(self):
        self.do_POST()
