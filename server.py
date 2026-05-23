#!/usr/bin/env python3
import http.server, json, os, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_FILE = os.path.join(os.path.dirname(__file__), "normies-chat.html")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {args[0]} {args[1]}")

    def do_GET(self):
        with open(HTML_FILE, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        api_key = self.headers.get("X-Api-Key", "")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp_body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Key")
        self.end_headers()

PORT = 3000
print("""
╔══════════════════════════════════════════╗
║         NORMIES CHAT — LOCAL SERVER      ║
╠══════════════════════════════════════════╣
║  Running at: http://localhost:3000       ║
║  Open that URL in any browser            ║
║  Press Ctrl+C to stop                   ║
╚══════════════════════════════════════════╝
""")
HTTPServer(("", PORT), Handler).serve_forever()
