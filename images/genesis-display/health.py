"""Temperature and memory readers plus the launch / in-game decisions. Thermal zone is found by type, never by number
(zone 7 on this laptop is the Wi-Fi chip). Never writes the CPU cap: host-tweaks owns it."""
import glob, os
from typing import Optional

MIN_MEM_MB = 500


def find_pkg_temp_zone(sysfs_root: str = "/sys/class/thermal") -> Optional[str]:
    for z in sorted(glob.glob(os.path.join(sysfs_root, "thermal_zone*"))):
        try:
            if open(os.path.join(z, "type")).read().strip() == "x86_pkg_temp":
                return z
        except OSError:
            pass
    return None


def read_temp_c(zone: Optional[str]) -> Optional[float]:
    if not zone:
        return None
    try:
        return int(open(os.path.join(zone, "temp")).read().strip()) / 1000.0
    except (OSError, ValueError):
        return None


def mem_available_mb(meminfo_path: str = "/proc/meminfo") -> Optional[int]:
    try:
        for line in open(meminfo_path):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


def launch_ok(temp_c: Optional[float], mem_mb: Optional[int]):
    if temp_c is None:
        return False, "temperature sensor unreadable, not starting a game"
    if mem_mb is None:
        return False, "memory figure unreadable, not starting a game"
    if mem_mb < MIN_MEM_MB:
        return False, "only %d MB of memory free (need %d), free some by stopping apps" % (mem_mb, MIN_MEM_MB)
    return True, "ok"


def ingame_action(temp_c: float) -> str:
    if temp_c >= 90: return "quit"
    if temp_c >= 85: return "warn"
    if temp_c >= 80: return "reduce"
    return "ok"
