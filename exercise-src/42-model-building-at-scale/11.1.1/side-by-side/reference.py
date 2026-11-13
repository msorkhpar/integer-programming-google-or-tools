from __future__ import annotations

import statistics
import time
from typing import Callable


def timed(work: Callable[[], object], clock: Callable[[], float]) -> float:
    """Seconds one run of `work` takes, read from `clock` just before and just after it."""
    began = clock()
    work()
    return clock() - began


def speedup(old: Callable[[], object], new: Callable[[], object], rounds: int = 5, warmup: int = 1,
            clock: Callable[[], float] = time.perf_counter) -> float:
    """How many times faster `new` is than `old`: the median, over rounds, of old's time / new's time."""
    for _ in range(warmup):
        old()
        new()
    ratios = [timed(old, clock) / timed(new, clock) for _ in range(rounds)]
    return statistics.median(ratios)


if __name__ == "__main__":
    def slow():
        return sum(i * i for i in range(200_000))

    def fast():
        return sum(i * i for i in range(20_000))

    print(f"fast is {speedup(slow, fast):.1f}x faster than slow on this machine, this time")
