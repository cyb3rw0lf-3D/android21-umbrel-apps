import os, sys, tempfile, time, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "images", "genesis-gate"))
import gate
from tests.fake_klippy import FakeKlippy


def run(mode, timeout=3.0):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "klippy.sock")
    with FakeKlippy(p, mode):
        return gate.check(p, timeout)


class GateTests(unittest.TestCase):
    def test_standby_allows(self):
        r = run("standby"); self.assertTrue(r.allow); self.assertEqual(r.state, "standby")

    def test_complete_and_cancelled_allow(self):
        for m in ("complete", "cancelled"):
            self.assertTrue(run(m).allow, m)

    def test_printing_refuses(self):
        self.assertFalse(run("printing").allow)

    def test_paused_refuses(self):
        self.assertFalse(run("paused").allow)

    def test_socket_absent_allows(self):
        r = gate.check("/nonexistent/klippy.sock")
        self.assertTrue(r.allow); self.assertIsNone(r.state)

    def test_error_reply_refuses(self):
        self.assertFalse(run("error_reply").allow)

    def test_garbled_reply_refuses(self):
        self.assertFalse(run("garbled").allow)

    def test_hang_refuses_within_4s(self):
        t = time.time(); r = run("hang", 3.0)
        self.assertLess(time.time() - t, 4); self.assertFalse(r.allow)

    def test_reason_text_mentions_printing(self):
        self.assertIn("printer is printing", run("printing").reason)


if __name__ == "__main__":
    unittest.main()
