import pytest

from compare import speedup


class Bench:
    """Two fake builders and a fake clock: each run of a builder moves the clock by the next duration."""

    def __init__(self, old_times, new_times):
        self.now = 0.0
        self.calls = []
        self.old_times, self.new_times = list(old_times), list(new_times)

    def clock(self):
        return self.now

    def old(self):
        self.calls.append("old")
        self.now += self.old_times.pop(0)

    def new(self):
        self.calls.append("new")
        self.now += self.new_times.pop(0)


def test_the_speedup_is_the_median_of_the_round_ratios():
    bench = Bench([9, 8.0, 12.0, 30.0], [9, 2.0, 3.0, 5.0])         # ratios 4, 4, 6
    assert speedup(bench.old, bench.new, rounds=3, warmup=1, clock=bench.clock) == pytest.approx(4.0)


def test_both_builders_warm_up_untimed_before_the_first_round():
    bench = Bench([100, 100, 8.0, 8.0], [100, 100, 2.0, 2.0])      # the warm-ups are slow and must not count
    assert speedup(bench.old, bench.new, rounds=2, warmup=2, clock=bench.clock) == pytest.approx(4.0)
    assert bench.calls[:4] == ["old", "new", "old", "new"]


def test_the_builders_alternate_round_by_round():
    bench = Bench([1, 6.0, 6.0, 6.0], [1, 2.0, 3.0, 1.0])
    speedup(bench.old, bench.new, rounds=3, warmup=1, clock=bench.clock)
    assert bench.calls == ["old", "new"] * 4


def test_an_even_number_of_rounds_takes_the_mean_of_the_middle_two():
    bench = Bench([1, 4.0, 6.0, 9.0, 20.0], [1, 2.0, 2.0, 1.0, 2.0])   # ratios 2, 3, 9, 10
    assert speedup(bench.old, bench.new, rounds=4, warmup=1, clock=bench.clock) == pytest.approx(6.0)


def test_each_ratio_is_taken_within_its_own_round():
    bench = Bench([1, 4.0, 10.0, 30.0], [1, 1.0, 5.0, 3.0])        # ratios 4, 2, 10
    assert speedup(bench.old, bench.new, rounds=3, warmup=1, clock=bench.clock) == pytest.approx(4.0)
