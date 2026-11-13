"""Does last cycle's plan help Gurobi? Every cycle, every seed, every kind of start, compared pairwise."""

from dataclasses import replace

from grb_runs import gurobi, quiet_env
from start_bench import KINDS, SEEDS, at_budgets, cycles, report

found = cycles()
env = quiet_env()
runs = {(c.name, seed, kind): gurobi(env, c.portfolio, seed, c.starts[kind])
        for c in found for seed in SEEDS for kind in KINDS}
# Gurobi's work unit is roughly a second, and these solves take hundredths of one: count thousandths.
milli = {key: replace(r, work=r.work * 1000, events=tuple((w * 1000, o) for w, o in r.events))
         for key, r in runs.items()}
print("Gurobi")
report(milli, shift=10, unit="thousandths of a work unit")
at_budgets(milli, (0, 1, 5, 20), "thousandths of a work unit")
again = [gurobi(env, c.portfolio, 1, c.starts["repaired"]) for c in found]
print("repaired start, seed 1, solved again: every run repeated:",
      all(a == runs[c.name, 1, "repaired"] for a, c in zip(again, found)))
