from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from .monitor import MonitorService

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

monitor = MonitorService(str(BASE_DIR / "config.json"))


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, code: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        data = self.rfile.read(length).decode("utf-8")
        return json.loads(data)

    def _serve_file(self, filename: str, content_type: str) -> None:
        path = STATIC_DIR / filename
        if not path.exists():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        route = urlparse(self.path).path
        if route in ("/", "/index.html"):
            self._serve_file("index.html", "text/html; charset=utf-8")
            return
        if route == "/app.js":
            self._serve_file("app.js", "application/javascript; charset=utf-8")
            return
        if route == "/styles.css":
            self._serve_file("styles.css", "text/css; charset=utf-8")
            return
        if route == "/api/status":
            self._json(monitor.status())
            return
        if route == "/api/config":
            self._json({"ok": True, "config": monitor.get_config(mask_sensitive=False)})
            return
        self.send_error(404)

    def do_POST(self):  # noqa: N802
        route = urlparse(self.path).path
        try:
            if route == "/api/start":
                monitor.start()
                self._json({"ok": True, "running": True})
                return
            if route == "/api/stop":
                monitor.stop()
                self._json({"ok": True, "running": False})
                return
            if route == "/api/check-now":
                results = [r.__dict__ for r in monitor.check_once()]
                self._json({"ok": True, "results": results})
                return
            if route == "/api/reload":
                monitor.reload_config()
                self._json({"ok": True})
                return
            if route == "/api/config":
                payload = self._read_json_body()
                monitor.save_config(payload)
                self._json({"ok": True})
                return
        except Exception as exc:  # pylint: disable=broad-except
            self._json({"ok": False, "error": str(exc)}, 400)
            return

        self.send_error(404)


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8899"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"VPS monitor dashboard running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
