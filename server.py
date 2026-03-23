"""
極輕量股價分析伺服器 — 只用 Python 標準函式庫，不需額外安裝。
啟動方式：python server.py
開啟瀏覽器：http://localhost:8080
"""

import http.server
import json
import os
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path

PORT = 8080
HTML_FILE = Path(__file__).parent / "index.html"


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html()
        elif self.path.startswith("/api/chart?"):
            self._proxy_yahoo()
        else:
            self.send_error(404)

    def _serve_html(self):
        content = HTML_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _proxy_yahoo(self):
        from urllib.parse import parse_qs, urlparse
        qs = parse_qs(urlparse(self.path).query)
        ticker = qs.get("ticker", [""])[0]
        rng = qs.get("range", ["1y"])[0]
        if not ticker:
            self.send_error(400, "Missing ticker")
            return
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self.send_error(e.code, str(e.reason))
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        # 簡化日誌
        print(f"  {args[0]}")


if __name__ == "__main__":
    if not HTML_FILE.exists():
        print(f"Error: {HTML_FILE} not found")
        exit(1)
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[OK] Stock chart server running: http://localhost:{PORT}")
    print("  Press Ctrl+C to stop")
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
