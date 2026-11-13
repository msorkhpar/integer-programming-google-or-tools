"""Time a piece of work honestly: warm up first, repeat, and keep every sample.

Wall-clock times differ between machines and between runs on one machine, so a timing is a
sample, not a fact. `measure` returns all the samples with their median and range; compare two
pieces of work by the ratio of their medians, measured in the same process, one after the other.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Timing:
    samples: tuple[float, ...]      # seconds, one per repeat, in the order they ran

    @property
    def median(self) -> float:
        return statistics.median(self.samples)

    @property
    def low(self) -> float:
        return min(self.samples)

    @property
    def high(self) -> float:
        return max(self.samples)

    def __str__(self) -> str:
        return f"median {self.median:.3f}s (range {self.low:.3f}-{self.high:.3f}, n={len(self.samples)})"


def measure(work: Callable[[], object], repeats: int = 5, warmup: int = 1,
            clock: Callable[[], float] = time.perf_counter) -> Timing:
    """Run `work` `warmup` times untimed, then `repeats` times, timing each run on its own."""
    for _ in range(warmup):
        work()
    samples = []
    for _ in range(repeats):
        start = clock()
        work()
        samples.append(clock() - start)
    return Timing(tuple(samples))


if __name__ == "__main__":
    from gridcap import generate
    from loop_builder import build_loops

    medium = generate("medium")
    start = time.perf_counter()
    build_loops(medium)
    first = time.perf_counter() - start
    timing = measure(lambda: build_loops(medium), repeats=7)
    print(f"first build, cold: {first:.3f}s")
    print("next 7 builds:", " ".join(f"{s:.3f}" for s in timing.samples))
    print("build_loops(medium):", timing)
    print(f"first build / median: {first / timing.median:.1f}x")
