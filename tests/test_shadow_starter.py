import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "images", "shadow-starter"))
import starter


class Clock:
    def __init__(self): self.t = 0.0
    def now(self): return self.t
    def sleep(self, s): self.t += s


def make(streaming_after=None, free=2000):
    c, calls = Clock(), []
    s = starter.Starter(launch=lambda: calls.append("launch"),
                        is_streaming=lambda: streaming_after is not None and c.t >= streaming_after,
                        stop=lambda: calls.append("stop"), free=lambda: free, sleep=c.sleep, now=c.now)
    return s, c, calls


class StarterTests(unittest.TestCase):
    def test_streams_then_closes_after_stay(self):
        s, c, calls = make(streaming_after=30)
        s.state = "opening"; s.run()
        self.assertEqual(calls, ["launch", "stop"])
        self.assertEqual(s.state, "idle")
        self.assertGreaterEqual(c.t, 30 + starter.STAY)

    def test_gives_up_if_it_never_streams(self):
        s, c, calls = make(streaming_after=None)
        s.state = "opening"; s.run()
        self.assertEqual(calls, ["launch", "stop"])
        self.assertEqual(s.state, "error")
        self.assertGreater(c.t, starter.CONNECT_TIMEOUT)

    def test_refuses_when_memory_is_low(self):
        s, _, calls = make(free=100)
        ok, msg = s.start()
        self.assertFalse(ok); self.assertIn("100 MB", msg); self.assertEqual(calls, [])

    def test_refuses_while_already_running(self):
        s, _, _ = make()
        s.state = "streaming"
        self.assertFalse(s.start()[0])


if __name__ == "__main__":
    unittest.main()
