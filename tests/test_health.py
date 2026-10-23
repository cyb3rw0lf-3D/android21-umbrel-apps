import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "images", "genesis-display"))
import health


def zones(**types):
    root = tempfile.mkdtemp()
    for name, (t, temp) in types.items():
        d = os.path.join(root, name); os.makedirs(d)
        open(os.path.join(d, "type"), "w").write(t + "\n")
        open(os.path.join(d, "temp"), "w").write(str(temp) + "\n")
    return root


class HealthTests(unittest.TestCase):
    def test_zone_found_by_type_not_number(self):
        r = zones(thermal_zone7=("iwlwifi_1", 40000), thermal_zone8=("x86_pkg_temp", 52000))
        z = health.find_pkg_temp_zone(r)
        self.assertTrue(z.endswith("thermal_zone8")); self.assertEqual(health.read_temp_c(z), 52.0)

    def test_no_pkg_zone_returns_none(self):
        self.assertIsNone(health.find_pkg_temp_zone(zones(thermal_zone7=("iwlwifi_1", 40000))))

    def test_mem_parse(self):
        p = tempfile.mktemp(); open(p, "w").write("MemTotal: 3500000 kB\nMemAvailable:    1048576 kB\n")
        self.assertEqual(health.mem_available_mb(p), 1024)

    def test_mem_file_missing_returns_none(self):
        self.assertIsNone(health.mem_available_mb("/nonexistent/meminfo"))

    def test_launch_refused_low_mem(self):
        self.assertFalse(health.launch_ok(50.0, 499)[0]); self.assertTrue(health.launch_ok(50.0, 500)[0])

    def test_launch_refused_when_sensor_missing(self):
        ok, msg = health.launch_ok(None, 900)
        self.assertFalse(ok); self.assertIn("sensor", msg)
        self.assertFalse(health.launch_ok(50.0, None)[0])

    def test_ingame_thresholds(self):
        self.assertEqual([health.ingame_action(t) for t in (79.9, 80, 85, 90)], ["ok", "reduce", "warn", "quit"])


if __name__ == "__main__":
    unittest.main()
