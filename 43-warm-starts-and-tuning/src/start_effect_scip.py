"""Does last cycle's plan help SCIP? Every cycle, every seed, with and without the repaired start."""

from runs import scip
from start_bench import SEEDS, at_budgets, cycles, report

found = cycles()
runs = {(c.name, seed, kind): scip(c.portfolio, seed, c.starts[kind])
        for c in found for seed in SEEDS for kind in ("none", "repaired")}
print("SCIP")
report(runs, shift=100, unit="LP iterations")
at_budgets(runs, (0, 50, 200, 1000), "LP iterations")
again = [scip(c.portfolio, 1, c.starts["repaired"]) for c in found]
print("repaired start, seed 1, solved again: every run repeated:",
      all(a == runs[c.name, 1, "repaired"] for a, c in zip(again, found)))
