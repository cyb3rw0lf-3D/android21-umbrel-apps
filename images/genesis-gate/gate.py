"""genesis-gate: may a game run? Reads print_stats.state from Klipper's API socket, read-only.

print_stats.state alone, never webhooks.state (that is MCU connectivity and is "error" whenever the printer is just off).
printing/paused refuse; socket absent allows (printer app stopped); socket present but unreadable refuses (unsure = no).
"""
import json, os, socket, time
from typing import NamedTuple, Optional

BLOCK = ("printing", "paused")


class Decision(NamedTuple):
    allow: bool
    state: Optional[str]
    reason: str


def check(sock_path: str, timeout: float = 3.0) -> Decision:
    if not os.path.exists(sock_path):
        return Decision(True, None, "printer app is not running")
    deadline = time.monotonic() + timeout
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.settimeout(timeout)
            s.connect(sock_path)
            req = {"id": 1, "method": "objects/query", "params": {"objects": {"print_stats": ["state"]}}}
            s.sendall(json.dumps(req).encode() + b"\x03")
            buf = b""
            while not buf.endswith(b"\x03"):
                left = deadline - time.monotonic()
                if left <= 0:
                    raise TimeoutError
                s.settimeout(left)
                d = s.recv(4096)
                if not d:
                    raise ConnectionError("closed before a full reply")
                buf += d
        finally:
            s.close()
        state = json.loads(buf[:-1])["result"]["status"]["print_stats"]["state"]
    except Exception:
        return Decision(False, None, "could not read the printer state, so not starting a game")
    if state in BLOCK:
        return Decision(False, state, "the printer is printing, try later" if state == "printing"
                        else "the printer is printing (paused), try later")
    return Decision(True, state, "printer idle")
