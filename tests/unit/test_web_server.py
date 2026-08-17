import pytest
import json
import urllib.request
import threading
import time
from http.server import ThreadingHTTPServer

from maclovin.web.server import DashboardHandler


@pytest.fixture(scope="module")
def local_web_server():
    server = ThreadingHTTPServer(("127.0.0.1", 8089), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield "http://127.0.0.1:8089"
    server.shutdown()
    server.server_close()


def test_web_index(local_web_server):
    with urllib.request.urlopen(f"{local_web_server}/") as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "Maclovin" in content
        assert "Radar de Ferramentas" in content


def test_web_api_briefing(local_web_server):
    with urllib.request.urlopen(f"{local_web_server}/api/briefing") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "date" in data
        assert "tools" in data
        assert "news" in data
        assert "learning" in data
        assert "geek" in data


def test_web_api_history(local_web_server):
    with urllib.request.urlopen(f"{local_web_server}/api/history") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "dates" in data
