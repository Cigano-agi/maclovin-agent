"""Local Web Server and REST API for Maclovin Daily Intelligence Dashboard."""

import http.server
import json
import urllib.parse
import pathlib
import mimetypes
from datetime import datetime, date
from typing import Optional

from maclovin.config import load_config
from maclovin.storage.database import get_db_connection
from maclovin.storage.log_repo import get_latest_execution
from maclovin.storage.news_repo import get_news_by_date
from maclovin.storage.supabase_client import (
    get_briefing_from_supabase,
    save_briefing_to_supabase,
    get_all_dates_from_supabase,
)
from maclovin.intelligence.factory import create_llm_provider
from maclovin.core.pipeline import Pipeline
from maclovin.reporting.markdown_parser import extract_briefing_from_markdown


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP para a plataforma web local."""

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

        # 1. API: Obter Briefing por Data (Supabase -> Markdown -> JSON)
        if path == "/api/briefing":
            target_date_str = query.get("date", [None])[0]
            
            # Tentar Supabase
            data = None
            try:
                data = get_briefing_from_supabase(target_date_str)
            except Exception:
                pass

            if not data:
                # Tentar Markdown
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
                    data = extract_briefing_from_markdown(selected_file)

            if not data:
                # Fallback JSON estático
                json_file = pathlib.Path(f"public/data/briefings/{target_date_str}.json" if target_date_str else "public/data/briefing.json")
                if json_file.exists():
                    try:
                        data = json.loads(json_file.read_text(encoding="utf-8"))
                    except Exception:
                        pass

            if not data:
                data = {
                    "date": target_date_str or datetime.now().strftime("%Y-%m-%d"),
                    "total_items": 0,
                    "tools": [],
                    "opportunities": [],
                    "business": [],
                    "learning": [],
                    "geek": [],
                    "news": [],
                }

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API: Histórico de Datas
        elif path == "/api/history":
            dates = []
            try:
                dates = get_all_dates_from_supabase()
            except Exception:
                pass

            if not dates:
                briefings_dir = pathlib.Path("briefings")
                if briefings_dir.exists():
                    dates = [f.stem for f in sorted(list(briefings_dir.glob("*.md")), reverse=True)]

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"dates": dates}).encode("utf-8"))
            return

        # 3. API: Status de Execução
        elif path == "/api/status":
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({
                "status": "ONLINE",
                "database": "Supabase PostgreSQL + SQLite",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }).encode("utf-8"))
            return

        # 4. Servir Arquivos Estáticos da Interface Web
        static_dir = pathlib.Path(__file__).parent / "static"
        if path == "/" or path == "/index.html":
            file_path = static_dir / "index.html"
        else:
            rel_path = path.lstrip("/")
            file_path = static_dir / rel_path

        if file_path.exists() and file_path.is_file():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            content_type = mime_type or "text/plain"
            if "text/" in content_type or "javascript" in content_type:
                content_type += "; charset=utf-8"
            self._set_headers(200, content_type)
            self.wfile.write(file_path.read_bytes())
            return

        self._set_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/run":
            cfg = load_config()
            provider = create_llm_provider(cfg.ai)
            pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=None)

            report = pipeline.run(dry_run=False)
            
            # Exportar e salvar no Supabase
            md_file = pathlib.Path(f"briefings/{report.reference_date.isoformat()}.md")
            if md_file.exists():
                payload = extract_briefing_from_markdown(md_file)
                try:
                    save_briefing_to_supabase(payload)
                except Exception:
                    pass

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({
                "status": "SUCCESS",
                "date": report.reference_date.isoformat(),
                "total_items": len(report.tools_and_launches) + len(report.opportunity_items) + len(report.business_items) + len(report.standalone_news) + len(report.learning_items) + len(report.geek_items)
            }).encode("utf-8"))
            return

        self._set_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"404 Not Found")


def run_web_server(port: int = 8000) -> None:
    """Inicia o servidor web da plataforma local."""
    server_address = ("", port)
    httpd = http.server.ThreadingHTTPServer(server_address, DashboardHandler)
    print(f"🚀 Plataforma Web Maclovin iniciada com sucesso!")
    print(f"🌐 Acesse no seu navegador em: http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando servidor web...")
        httpd.server_close()
