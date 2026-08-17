"""Vercel Serverless Function for /api/history."""

import http.server
import json
import pathlib


class handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        briefings_dir = pathlib.Path("briefings")
        dates = []
        if briefings_dir.exists():
            for f in sorted(list(briefings_dir.glob("*.md")), reverse=True):
                dates.append(f.stem)

        if not dates:
            dates = ["2026-08-16"]

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"dates": dates}).encode("utf-8"))
