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
from maclovin.intelligence.factory import create_llm_provider
from maclovin.core.pipeline import Pipeline


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

        # 1. API: Obter Briefing por Data
        if path == "/api/briefing":
            cfg = load_config()
            conn = get_db_connection(cfg.settings.database_path)
            
            target_date_str = query.get("date", [None])[0]
            if target_date_str:
                try:
                    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                except ValueError:
                    target_date = None
            else:
                from maclovin.core.clock import get_yesterday_window
                _, _, target_date = get_yesterday_window(cfg.settings.timezone)

            items = get_news_by_date(conn, target_date)
            latest = get_latest_execution(conn)
            conn.close()

            # Separar por categorias usando model_dump(mode="json") para serialização de datas
            tools = [it.model_dump(mode="json") for it in items if it.item_type == "tool"]
            learning = [it.model_dump(mode="json") for it in items if it.item_type == "learning"]
            geek = [it.model_dump(mode="json") for it in items if it.item_type == "geek"]
            news = [it.model_dump(mode="json") for it in items if it.item_type == "news"]

            payload = {
                "date": target_date.isoformat(),
                "total_items": len(items),
                "tools": tools,
                "learning": learning,
                "geek": geek,
                "news": news,
                "latest_execution": latest,
            }
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API: Histórico de Datas
        elif path == "/api/history":
            cfg = load_config()
            out_dir = pathlib.Path(cfg.settings.output_dir)
            dates = []
            if out_dir.exists():
                for f in out_dir.glob("*.md"):
                    date_part = f.stem
                    dates.append(date_part)
            dates.sort(reverse=True)
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"dates": dates}).encode("utf-8"))
            return

        # 3. API: Status de Execução
        elif path == "/api/status":
            cfg = load_config()
            conn = get_db_connection(cfg.settings.database_path)
            latest = get_latest_execution(conn)
            conn.close()
            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(latest or {}).encode("utf-8"))
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
            conn = get_db_connection(cfg.settings.database_path)
            provider = create_llm_provider(cfg.ai)
            pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=conn)

            report = pipeline.run(dry_run=False)
            conn.close()

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps({"status": "SUCCESS", "date": report.reference_date.isoformat(), "stats": report.execution_stats}).encode("utf-8"))
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
