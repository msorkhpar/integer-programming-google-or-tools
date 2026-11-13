"""Does last cycle's plan help HiGHS? Every cycle, every seed, three kinds of start, compared pairwise."""

from runs import highs
from start_bench import SEEDS, at_budgets, cycles, report

found = cycles()
runs = {(c.name, seed, kind): highs(c.portfolio, seed, c.starts[kind])
        for c in found for seed in SEEDS for kind in ("none", "repaired", "greedy")}
print("HiGHS")
report(runs, shift=100, unit="LP iterations")
at_budgets(runs, (0, 50, 200, 1000), "LP iterations")
again = [highs(c.portfolio, 1, c.starts["repaired"]) for c in found]
print("repaired start, seed 1, solved again: every run repeated:",
      all(a == runs[c.name, 1, "repaired"] for a, c in zip(again, found)))
