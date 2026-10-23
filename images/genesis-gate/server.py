"""Loopback HTTP wrapper: GET /gate -> {"allow","state","reason"} (always HTTP 200)."""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import gate

SOCK = os.environ.get("KLIPPY_SOCK", "/comms/klippy.sock")
BIND = os.environ.get("GATE_BIND", "0.0.0.0")   # reachable on the app network only; no port is published


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] != "/gate":
            self.send_response(404); self.end_headers(); return
        body = json.dumps(gate.check(SOCK)._asdict()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer((BIND, 8210), H).serve_forever()
