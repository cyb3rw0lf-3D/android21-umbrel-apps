import json, os, unittest
D = os.path.join(os.path.dirname(__file__), "..", "images", "genesis-display")
DEBIAN_CORES = {"nestopia_libretro.so", "mgba_libretro.so", "desmume_libretro.so"}


class SystemsTests(unittest.TestCase):
    def setUp(self):
        self.systems = json.load(open(os.path.join(D, "systems.json")))

    def test_every_system_has_core_and_exts(self):
        for n, s in self.systems.items():
            self.assertTrue(s["core"].endswith("_libretro.so"), n)
            self.assertTrue(s["exts"] and all(e.startswith(".") for e in s["exts"]), n)

    def test_core_files_exist_in_lock_or_debian_list(self):
        lock = {l.split()[0] + "_libretro.so" for l in open(os.path.join(D, "cores.lock"))
                if l.strip() and not l.startswith("#")}
        for n, s in self.systems.items():
            self.assertIn(s["core"], lock | DEBIAN_CORES, n)

    def test_template_has_network_cmd_and_autoconfig(self):
        t = open(os.path.join(D, "retroarch.cfg.tmpl")).read()
        self.assertIn('network_cmd_enable = "true"', t); self.assertIn('network_cmd_port = "55355"', t)
        self.assertIn('joypad_autoconfig_dir = "/opt/autoconfig"', t)


if __name__ == "__main__":
    unittest.main()
