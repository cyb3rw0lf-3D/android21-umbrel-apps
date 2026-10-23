import os, sys, threading, time, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "images", "genesis-display"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "images", "genesis-gate"))
from gate import Decision
import supervisor

SYSTEMS = {"nes": {"core": "nestopia_libretro.so", "exts": [".nes"]}}
ALLOW = Decision(True, "standby", "printer idle")
BLOCK = Decision(False, "printing", "the printer is printing, try later")


class Proc:
    def __init__(self, exits_on_quit=True):
        self.exits_on_quit, self.alive, self.killed = exits_on_quit, True, False
    def poll(self): return None if self.alive else 0
    def kill(self): self.killed, self.alive = True, False


class Rig:
    def __init__(self, gate=ALLOW, temp=50.0, mem=900, exits_on_quit=True, grace=0.3):
        self.gate, self.temp, self.cmds, self.spawned = gate, temp, [], []
        self.exits_on_quit = exits_on_quit
        def spawn(argv):
            self.spawned.append(argv); self.proc = Proc(exits_on_quit); return self.proc
        def send(cmd):
            self.cmds.append(cmd)
            if cmd == "QUIT" and self.exits_on_quit: self.proc.alive = False
        self.sup = supervisor.Supervisor(lambda: self.gate, spawn, send, SYSTEMS, grace_s=grace, save_wait_s=0,
                                         temp_fn=lambda: self.temp, mem_fn=lambda: mem)


class SupervisorTests(unittest.TestCase):
    def test_launch_refused_when_gate_refuses(self):
        r = Rig(gate=BLOCK); res = r.sup.launch("nes", "/roms/a.nes")
        self.assertFalse(res.ok); self.assertIn("printing", res.reason); self.assertEqual(r.spawned, [])

    def test_launch_allowed_spawns_once(self):
        r = Rig(); self.assertTrue(r.sup.launch("nes", "/roms/a.nes").ok); self.assertEqual(len(r.spawned), 1)
        self.assertTrue(r.sup.running)

    def test_second_launch_while_running_refused(self):
        r = Rig(); r.sup.launch("nes", "/roms/a.nes")
        self.assertFalse(r.sup.launch("nes", "/roms/b.nes").ok); self.assertEqual(len(r.spawned), 1)

    def test_concurrent_launches_spawn_one(self):
        r = Rig(); ts = [threading.Thread(target=r.sup.launch, args=("nes", "/roms/a.nes")) for _ in range(8)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(len(r.spawned), 1)

    def test_print_starts_midgame_saves_then_quits(self):
        r = Rig(); r.sup.launch("nes", "/roms/a.nes"); r.gate = BLOCK; r.sup.tick()
        self.assertEqual(r.cmds, ["SAVE_STATE", "QUIT"]); self.assertFalse(r.sup.running)

    def test_quit_ignored_gets_killed_after_grace(self):
        r = Rig(exits_on_quit=False); r.sup.launch("nes", "/roms/a.nes"); r.gate = BLOCK
        t = time.time(); r.sup.tick()
        self.assertTrue(r.proc.killed); self.assertGreaterEqual(time.time() - t, 0.3); self.assertFalse(r.sup.running)

    def test_rom_name_is_single_argv_element(self):
        for name in ("a b.nes", "x';rm -rf ~;'.nes", "$(id).nes", "-evil.nes"):
            r = Rig(); r.sup.launch("nes", "/roms/" + name if not name.startswith("-") else name)
            argv = r.spawned[0]
            self.assertEqual(argv.count(name if name.startswith("-") else "/roms/" + name), 1, argv)
            self.assertEqual(argv[-2], "--"); self.assertEqual(argv[:3], ["nice", "-n", "5"])

    def test_unknown_system_refused(self):
        r = Rig(); self.assertFalse(r.sup.launch("atari9000", "/roms/a.bin").ok); self.assertEqual(r.spawned, [])

    def test_wrong_extension_refused(self):
        r = Rig(); self.assertFalse(r.sup.launch("nes", "/roms/a.exe").ok)

    def test_low_memory_refuses_launch(self):
        r = Rig(mem=300); self.assertFalse(r.sup.launch("nes", "/roms/a.nes").ok)

    def test_supervisor_quits_at_90c(self):
        r = Rig(); r.sup.launch("nes", "/roms/a.nes"); r.temp = 91.0; r.sup.tick()
        self.assertEqual(r.cmds, ["SAVE_STATE", "QUIT"])

    def test_game_exit_clears_running(self):
        r = Rig(); r.sup.launch("nes", "/roms/a.nes"); r.proc.alive = False; r.sup.tick()
        self.assertFalse(r.sup.running)


if __name__ == "__main__":
    unittest.main()
