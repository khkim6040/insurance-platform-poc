#!/usr/bin/env python3
"""External rating API stub. GET /rate?delayMs=N -> {"rate": 1.2} after N ms.
Default delay comes from STUB_DELAY_MS (ms). Port from argv[1], default 9090."""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/rate":
            self.send_error(404)
            return
        default_delay = os.environ.get("STUB_DELAY_MS", "0")
        delay_ms = int(parse_qs(url.query).get("delayMs", [default_delay])[0])
        time.sleep(delay_ms / 1000)
        body = json.dumps({"rate": 1.2}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9090
    print(f"stub listening on 127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
