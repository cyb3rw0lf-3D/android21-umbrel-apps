"""Opens the official Shadow app, waits until it is streaming (which turns the Shadow PC on), then closes it.

The app's own "Start streaming automatically" setting does the connecting; this only opens and closes it.
"""
import os, signal, subprocess, threading, time

LAUNCH = ["/usr/bin/shadow-prod", "--no-sandbox"]
STREAMER = "ShadowPCDisplay"          # the app's native renderer; it only runs while streaming
STAY = int(os.environ.get("SHADOW_STAY_SECONDS", "120"))
CONNECT_TIMEOUT = int(os.environ.get("SHADOW_CONNECT_TIMEOUT", "300"))
MIN_FREE_MB = int(os.environ.get("SHADOW_MIN_FREE_MB", "600"))


def free_mb():
    with open("/proc/meminfo") as f:
        info = dict(line.split(":", 1) for line in f)
    return int(info["MemAvailable"].split()[0]) // 1024


def running(name):
    return subprocess.run(["pgrep", "-f", name], capture_output=True).returncode == 0


def stop_app():
    for name in (STREAMER, "shadow-launcher"):
        subprocess.run(["pkill", "-TERM", "-f", name], capture_output=True)
    time.sleep(5)
    for name in (STREAMER, "shadow-launcher"):
        subprocess.run(["pkill", "-KILL", "-f", name], capture_output=True)


class Starter:
    def __init__(self, launch=lambda: subprocess.Popen(LAUNCH, start_new_session=True), is_streaming=lambda: running(STREAMER),
                 stop=stop_app, free=free_mb, sleep=time.sleep, now=time.time):
        self.launch, self.is_streaming, self.stop, self.free, self.sleep, self.now = launch, is_streaming, stop, free, sleep, now
        self.lock = threading.Lock()
        self.state, self.message, self.last = "idle", "Ready.", None

    def status(self):
        return {"state": self.state, "message": self.message, "last_started": self.last}

    def start(self):
        """Begin a run in the background. Returns (accepted, message)."""
        with self.lock:
            if self.state in ("opening", "streaming"):
                return False, "Already starting."
            if self.free() < MIN_FREE_MB:
                return False, f"Only {self.free()} MB of memory free. Stop Firefox, Cura or a slicer first."
            self.state, self.message = "opening", "Opening the Shadow app..."
        threading.Thread(target=self.run, daemon=True).start()
        return True, "Starting."

    def open_for_signin(self):
        """Open the app and leave it open (for signing in or changing its settings)."""
        with self.lock:
            if self.state in ("opening", "streaming"):
                return False, "Already starting."
            self.launch()
            self.message = "The Shadow app is open on the desktop. Close it there when you're done."
        return True, "Opened."

    def run(self):
        self.launch()
        deadline = self.now() + CONNECT_TIMEOUT
        while not self.is_streaming():
            if self.now() > deadline:
                self.stop()
                self.state = "error"
                self.message = ("The Shadow app didn't start streaming. Open the desktop to check it's signed in "
                                "and that 'Start streaming automatically' is on.")
                return
            self.sleep(3)
        self.state, self.message, self.last = "streaming", f"Connected. Closing in {STAY // 60} min.", self.now()
        self.sleep(STAY)
        self.stop()
        self.state, self.message = "idle", "Your Shadow PC should be on. Connect with Avica."
