"""Comparing two settings of one solver in its own deterministic unit, over instances and seeds (lesson 5.4.2).

Within one solver, a deterministic unit is a fair yardstick: LP iterations of HiGHS with presolve
on and off measure the same thing. The question: does switching HiGHS's presolve off help on
GridCap's instance set? Each (instance, seed) pair is one paired observation.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from instances import instance_set
from sgm import shifted_geometric_mean
from solvers import run

SEEDS = (1, 2, 3)
SHIFT = 100.0

on, off, rows = [], [], []
for inst in instance_set():
    for seed in SEEDS:
        a = run("HiGHS", inst, seed)
        b = run("HiGHS", inst, seed, presolve=mathopt.Emphasis.OFF)
        assert round(a.objective) == round(b.objective)
        on.append(a.work["lp_iterations"])
        off.append(b.work["lp_iterations"])
        rows.append((inst.name, seed, on[-1], off[-1]))

print(f"{'instance':<18} {'seed':>4} {'presolve on':>12} {'off':>8} {'off/on':>7}")
for name, seed, a, b in rows:
    print(f"{name:<18} {seed:>4} {a:>12,} {b:>8,} {b / a:>7.2f}")

print("\nwhat one seed alone would conclude (SGM of off / SGM of on, shift 100):")
for seed in SEEDS:
    pick = [i for i, r in enumerate(rows) if r[1] == seed]
    ratio = (shifted_geometric_mean([off[i] for i in pick], SHIFT)
             / shifted_geometric_mean([on[i] for i in pick], SHIFT))
    print(f"  seed {seed}: {ratio:.3f}")
ratio = shifted_geometric_mean(off, SHIFT) / shifted_geometric_mean(on, SHIFT)
better = sum(b < a for _, _, a, b in rows)
worse = sum(b > a for _, _, a, b in rows)
print(f"all {len(rows)} pairs:  {ratio:.3f}; presolve off used fewer LP iterations in {better}, more in {worse}")
