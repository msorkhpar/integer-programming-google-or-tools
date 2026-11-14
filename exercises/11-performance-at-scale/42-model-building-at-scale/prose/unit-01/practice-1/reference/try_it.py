"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from compare import speedup


class Bench:
    """A pretend clock: each builder run moves it by the next duration in its list."""

    def __init__(self, old_times, new_times):
        self.now = 0.0
        self.old_times, self.new_times = list(old_times), list(new_times)

    def clock(self):
        return self.now

    def old(self):
        self.now += self.old_times.pop(0)

    def new(self):
        self.now += self.new_times.pop(0)


bench = Bench([50, 10.0, 15.0, 40.0], [50, 5.0, 3.0, 4.0])
print("speedup, rounds 3 ratios 2/5/10:", speedup(bench.old, bench.new, rounds=3, warmup=1, clock=bench.clock))
bench = Bench([6.0, 6.0], [2.0, 1.0])
print("speedup, no warm-up, ratios 3/6:", speedup(bench.old, bench.new, rounds=2, warmup=0, clock=bench.clock))
