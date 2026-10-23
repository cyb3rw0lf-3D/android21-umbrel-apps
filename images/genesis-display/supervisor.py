"""Launch, watch and stop one game. The gate is consulted before launch and on every tick; a print starting (or 90 C)
saves state and quits. RetroArch runs at nice 5, started by argv list (never a shell) so ROM names cannot inject commands."""
import os, socket, threading, time
from typing import Callable, NamedTuple

import health

CMD_ADDR = ("127.0.0.1", 55355)      # RetroArch network command interface (network_cmd_enable in the cfg)


class LaunchResult(NamedTuple):
    ok: bool
    reason: str


def build_argv(system: str, rom_path: str, systems: dict, cores_dir: str = "/cores") -> list:
    core = os.path.join(cores_dir, systems[system]["core"])
    return ["nice", "-n", "5", "retroarch", "-L", core, "--", rom_path]


def send_udp(cmd: str) -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(cmd.encode(), CMD_ADDR)
    finally:
        s.close()


class Supervisor:
    def __init__(self, gate_fn: Callable, spawn_fn: Callable, send_cmd_fn: Callable, systems: dict,
                 poll_s: float = 5, grace_s: float = 5, save_wait_s: float = 0.5, cores_dir: str = "/cores",
                 temp_fn: Callable = None, mem_fn: Callable = None):
        self.gate_fn, self.spawn_fn, self.send = gate_fn, spawn_fn, send_cmd_fn
        self.systems, self.poll_s, self.grace_s, self.cores_dir = systems, poll_s, grace_s, cores_dir
        self.save_wait_s = save_wait_s
        self.temp_fn = temp_fn or (lambda: health.read_temp_c(health.find_pkg_temp_zone()))
        self.mem_fn = mem_fn or health.mem_available_mb
        self._lock = threading.Lock()
        self._proc = None

    @property
    def running(self) -> bool:
        return self._proc is not None

    def launch(self, system: str, rom_path: str) -> LaunchResult:
        with self._lock:
            if self._proc is not None:
                return LaunchResult(False, "a game is already running")
            spec = self.systems.get(system)
            if spec is None:
                return LaunchResult(False, "unknown system")
            if os.path.splitext(rom_path)[1].lower() not in spec.get("exts", []):
                return LaunchResult(False, "not a %s file" % system)
            d = self.gate_fn()
            if not d.allow:
                return LaunchResult(False, d.reason)
            ok, why = health.launch_ok(self.temp_fn(), self.mem_fn())
            if not ok:
                return LaunchResult(False, why)
            self._proc = self.spawn_fn(build_argv(system, rom_path, self.systems, self.cores_dir))
            return LaunchResult(True, "started")

    def tick(self) -> None:
        with self._lock:
            p = self._proc
        if p is None:
            return
        if p.poll() is not None:
            with self._lock:
                self._proc = None
            return
        d = self.gate_fn()
        if not d.allow:
            return self.stop(d.reason)
        t = self.temp_fn()
        if t is None or health.ingame_action(t) == "quit":
            return self.stop("too hot" if t is not None else "temperature sensor lost")

    def stop(self, reason: str) -> None:
        with self._lock:
            p = self._proc
        if p is None:
            return
        self.send("SAVE_STATE")
        time.sleep(self.save_wait_s)          # let RetroArch finish writing the state before QUIT
        self.send("QUIT")
        end = time.monotonic() + self.grace_s
        while p.poll() is None and time.monotonic() < end:
            time.sleep(0.05)
        if p.poll() is None:
            p.kill()
        with self._lock:
            self._proc = None

    def run_forever(self) -> None:
        while True:
            self.tick()
            time.sleep(self.poll_s)
