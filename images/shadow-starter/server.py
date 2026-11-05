"""Start page and API: GET / (buttons), POST /api/start, POST /api/open (sign-in), GET /api/status."""
import html, json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from starter import Starter

starter = Starter()
DESKTOP_URL = os.environ.get("SHADOW_DESKTOP_URL", "")

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Shadow Starter</title><style>body{{font-family:system-ui,sans-serif;max-width:32rem;margin:3rem auto;padding:0 1rem}}
button{{font-size:1.2rem;padding:.8rem 1.6rem;border-radius:.5rem;border:0;background:#4b5ef5;color:#fff;cursor:pointer}}
button:disabled{{opacity:.5}}button.alt{{font-size:1rem;background:#666}}p.s{{color:#555}}</style>
<h1>Shadow Starter</h1><p class=s id=msg>{message}</p>
<form method=post action=/api/start><button {disabled}>Start Shadow PC</button></form>
<p><a href="{desktop}">Open the Shadow app's desktop</a> (sign in, settings)</p>
<form method=post action=/api/open><button class=alt {disabled}>Open the Shadow app to sign in</button></form>
<script>setTimeout(()=>location.reload(),5000)</script>"""


class H(BaseHTTPRequestHandler):
    def reply(self, code, body, kind="application/json"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/status":
            return self.reply(200, json.dumps(starter.status()))
        if path == "/":
            s = starter.status()
            busy = s["state"] in ("opening", "streaming")
            return self.reply(200, PAGE.format(message=html.escape(s["message"]), disabled="disabled" if busy else "",
                                               desktop=html.escape(DESKTOP_URL)), "text/html; charset=utf-8")
        self.reply(404, "{}")

    def do_POST(self):
        path = self.path.split("?")[0]
        if path not in ("/api/start", "/api/open"):
            return self.reply(404, "{}")
        ok, message = starter.start() if path == "/api/start" else starter.open_for_signin()
        if "application/json" in (self.headers.get("Accept") or "") or self.headers.get("Content-Type") == "application/json":
            return self.reply(202 if ok else 409, json.dumps({"accepted": ok, "message": message}))
        self.send_response(303); self.send_header("Location", "/"); self.end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8213), H).serve_forever()
