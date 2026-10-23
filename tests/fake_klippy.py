"""Fake Klippy API socket for gate tests. Frames are JSON terminated by 0x03, like the real klippy.sock."""
import json, os, socket, threading, time

class FakeKlippy:
    STATES = ("standby", "printing", "paused", "complete", "cancelled", "error")

    def __init__(self, path, mode):
        self.path, self.mode = path, mode

    def __enter__(self):
        self.srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.srv.bind(self.path)
        self.srv.listen(4)
        self._stop = False
        self.t = threading.Thread(target=self._loop, daemon=True)
        self.t.start()
        return self

    def __exit__(self, *a):
        self._stop = True
        self.srv.close()

    def _loop(self):
        while not self._stop:
            try:
                c, _ = self.srv.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(c,), daemon=True).start()

    def _serve(self, c):
        buf = b""
        while not buf.endswith(b"\x03"):
            d = c.recv(4096)
            if not d:
                return
            buf += d
        rid = json.loads(buf[:-1])["id"]
        if self.mode == "hang":
            time.sleep(10)
        elif self.mode == "garbled":
            c.sendall(b'{"id": 1, "result": {"stat\x03')
        elif self.mode == "error_reply":
            c.sendall(json.dumps({"id": rid, "error": {"message": "boom"}}).encode() + b"\x03")
        else:
            c.sendall(json.dumps({"id": rid, "result": {"status": {"print_stats": {"state": self.mode}}}}).encode() + b"\x03")
        c.close()
