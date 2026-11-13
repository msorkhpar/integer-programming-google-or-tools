"""Does a start help? Every regional plan, rolled forward one cycle, solved with and without each kind of start.

The instance set is fixed before any run: the eight regional plans of `plan_model.instance_set`,
each solved to optimality for its 2027 cycle (that plan is "last cycle's plan") and rolled forward
with `next_cycle(..., seed=7)`. Each next-cycle model is then solved by one solver with seeds 1, 2
and 3, once per kind of start:

- none: no start;
- carried: last cycle's plan carried forward as it is (it may break this cycle's rows);
- repaired: carried forward, repaired, then greedily filled (`starts.py`);
- greedy: built from nothing by the greedy rule (`starts.greedy_plan`).

Each (instance, seed) is one paired observation. Measures, in the solver's deterministic unit:
the gap of the first plan to the instance's best known value, the work until a plan within 1% of it,
and the total work to prove optimality.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from cycles import next_cycle
from plan_model import instance_set, keys
from runs import Run, hint_values, highs
from sgm import compare, shifted_geometric_mean
from starts import carry_forward, greedy_fill, greedy_plan, repair

SEEDS = (1, 2, 3)
KINDS = ("none", "carried", "repaired", "greedy")


@dataclass(frozen=True)
class Cycle:
    name: str
    portfolio: object                # next cycle's Portfolio
    starts: dict                     # kind -> {(project, year): value} or None


def cycles() -> list[Cycle]:
    """The fixed set: each regional plan's next cycle, with its four kinds of start."""
    found = []
    for pf in instance_set():
        last = highs(pf, 1).plan                       # the approved 2027 plan (proved optimal)
        nxt, _ = next_cycle(pf, last, seed=7)
        carried, _ = carry_forward(last, nxt)
        k = keys(nxt)
        found.append(Cycle(pf.name, nxt, {
            "none": None,
            "carried": hint_values(k, carried),
            "repaired": hint_values(k, greedy_fill(nxt, repair(nxt, carried))),
            "greedy": hint_values(k, greedy_plan(nxt)),
        }))
    return found


def first_gap(run: Run, best: float) -> float:
    return (best - run.events[0][1]) / abs(best) if run.events else math.inf


def report(runs: dict[tuple[str, int, str], Run], shift: float, unit: str) -> None:
    """Print one row per kind of start, each compared pairwise with no start."""
    best = best_known(runs)
    pairs = sorted({(name, seed) for name, seed, _ in runs})
    kinds = [k for k in KINDS if any(key[2] == k for key in runs)]
    print(f"{'start':<9} {'to first plan':>13} {'its gap':>8}  {'to 1%':>6} {'vs none':>8} {'W/L':>6}  "
          f"{'to proof':>8} {'vs none':>8} {'W/L':>6}")
    for kind in kinds:
        first = [runs[n, s, kind].first() for n, s in pairs]
        gaps = [first_gap(runs[n, s, kind], best[n]) for n, s in pairs]
        to1 = [runs[n, s, kind].within(best[n], 0.01) for n, s in pairs]
        to1_none = [runs[n, s, "none"].within(best[n], 0.01) for n, s in pairs]
        proof = [runs[n, s, kind].work for n, s in pairs]
        proof_none = [runs[n, s, "none"].work for n, s in pairs]
        r1, w1, l1 = compare(to1, to1_none, shift)
        rp, wp, lp = compare(proof, proof_none, shift)
        print(f"{kind:<9} {shifted_geometric_mean(first, shift):>13,.0f} {sum(gaps) / len(gaps):>8.1%}  "
              f"{shifted_geometric_mean(to1, shift):>6,.0f} {r1:>8.2f} {w1:>2}/{l1:<3}  "
              f"{shifted_geometric_mean(proof, shift):>8,.0f} {rp:>8.2f} {wp:>2}/{lp:<3}")
    print(f"({len(pairs)} paired observations: {len(best)} cycles x {len(SEEDS)} seeds; work in {unit};")
    print(f" shifted geometric means, shift {shift:g}; W/L: runs with less/more work than with no start)")


def best_known(runs: dict[tuple[str, int, str], Run]) -> dict[str, float]:
    """Each cycle's optimum, from the runs that proved it."""
    best = {}
    for (name, _, _), r in runs.items():
        if r.status == "optimal":
            best[name] = max(best.get(name, -math.inf), r.objective)
    return best


def best_by(run: Run, budget: float) -> float:
    """The best plan's value found within `budget` units of work, or -inf if none was."""
    found = [objective for work, objective in run.events if work <= budget]
    return max(found) if found else -math.inf


def at_budgets(runs: dict[tuple[str, int, str], Run], budgets: tuple[float, ...], unit: str) -> None:
    """Mean gap of the best plan in hand after each amount of work: what a stopped solve would return."""
    best = best_known(runs)
    pairs = sorted({(name, seed) for name, seed, _ in runs})
    kinds = [k for k in KINDS if any(key[2] == k for key in runs)]
    print(f"mean gap of the best plan in hand, by work done ({unit}):")
    print(f"{'start':<9}" + "".join(f"{b:>10g}" for b in budgets))
    for kind in kinds:
        cells = []
        for b in budgets:
            gaps = [(best[n] - best_by(runs[n, s, kind], b)) / abs(best[n]) for n, s in pairs]
            cells.append("no plan" if any(math.isinf(g) for g in gaps) else f"{sum(gaps) / len(gaps):.2%}")
        print(f"{kind:<9}" + "".join(f"{c:>10}" for c in cells))
