import hashlib, os, re, subprocess, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
D = os.path.join(os.path.dirname(__file__), "..", "images", "genesis-display")


def rows():
    return [l.split() for l in open(os.path.join(D, "cores.lock")) if l.strip() and not l.startswith("#")]


class LockTests(unittest.TestCase):
    def test_lock_has_all_fields(self):
        for r in rows():
            self.assertGreaterEqual(len(r), 6, r)
            self.assertTrue(re.fullmatch(r"[\w.-]+/[\w.-]+", r[1]), r)

    def test_commits_are_40_hex(self):
        for r in rows():
            self.assertRegex(r[2], r"^[0-9a-f]{40}$", r)

    def test_no_branch_names(self):
        for r in rows():
            self.assertNotIn(r[2], ("master", "main", "HEAD"))

    def test_verify_detects_tampered_core(self):
        d = tempfile.mkdtemp()
        lock = os.path.join(D, "cores.lock")
        # a copy of the lock whose recorded checksum for snes9x is of known bytes, then the file is different
        good = b"good"
        t = tempfile.mkdtemp()
        for f in ("verify-cores.sh",):
            open(os.path.join(t, f), "w").write(open(os.path.join(D, f)).read()); os.chmod(os.path.join(t, f), 0o755)
        open(os.path.join(t, "cores.lock"), "w").write("snes9x a/b %s %s . Makefile\n" % ("0" * 40, hashlib.sha256(good).hexdigest()))
        open(os.path.join(d, "snes9x_libretro.so"), "wb").write(b"evil")
        r = subprocess.run([os.path.join(t, "verify-cores.sh"), d], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0); self.assertIn("MISMATCH", r.stdout)
        open(os.path.join(d, "snes9x_libretro.so"), "wb").write(good)
        self.assertEqual(subprocess.run([os.path.join(t, "verify-cores.sh"), d]).returncode, 0)

    def test_build_refuses_when_gate_says_printing(self):
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                b = b'{"allow": false, "state": "printing", "reason": "the printer is printing, try later"}'
                self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            def log_message(self, *a): pass
        srv = HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
        out = tempfile.mkdtemp()
        env = dict(os.environ, GATE_URL="http://127.0.0.1:%d/gate" % srv.server_port, WORK=os.path.join(out, "w"))
        r = subprocess.run([os.path.join(D, "build-cores.sh"), out], env=env, capture_output=True, text=True)
        srv.shutdown()
        self.assertEqual(r.returncode, 3); self.assertFalse(os.path.exists(os.path.join(out, "w", "snes9x")))

    def test_build_refuses_when_gate_unreachable(self):
        out = tempfile.mkdtemp()
        env = dict(os.environ, GATE_URL="http://127.0.0.1:1/gate", WORK=os.path.join(out, "w"))
        self.assertEqual(subprocess.run([os.path.join(D, "build-cores.sh"), out], env=env, capture_output=True).returncode, 3)


if __name__ == "__main__":
    unittest.main()
