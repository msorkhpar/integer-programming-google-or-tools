"""A benchmark harness: every solver on every instance with every seed, summarized by shifted geometric means.

Lesson 5.4.2 builds it; lesson 5.4.4 writes a recommendation from its output. The rules it follows:
- one formulation, one thread, one gap target (0) for every solver;
- each (solver, instance, seed) runs twice, and a measure counts only if both runs agree on it;
- a run that does not finish counts at the cap, as Mittelmann's pages count non-successes;
- each solver is summarized in its own deterministic unit, so the numbers repeat; units of different
  solvers are not comparable, so across solvers only wall time compares, and it never repeats;
  it is computed here and printed masked.
"""

from __future__ import annotations

from dataclasses import dataclass

from instances import Instance, build_mathopt, instance_set
from sgm import shifted_geometric_mean
from solvers import MEASURES, TAKES_SEED, Run, run

SEEDS = (1, 2, 3)
SOLVERS = ("HiGHS", "SCIP", "CP-SAT", "CBC")
#: The unit each measure is counted in, and what one reported unit is worth in it. The mean's
#: max(1, v + shift) needs even the easiest instances to cost well above 1, so CP-SAT's
#: deterministic time, often a few ten-thousandths, is counted in millionths.
UNIT = {"lp_iterations": ("lp_iterations", 1), "det_time": ("micro_det_time", 1_000_000)}
#: The shift for each counted unit: about what the easiest instances in the set cost.
SHIFT = {"lp_iterations": 100.0, "det_time": 100.0}
#: What an unfinished run counts as, in each counted unit (1,000 deterministic seconds for CP-SAT).
CAP = {"lp_iterations": 10_000_000.0, "det_time": 1_000_000_000.0}
WALL_SHIFT = 1.0


@dataclass(frozen=True)
class Cell:
    """The runs of one solver on one instance with one seed, and whether they repeated."""
    first: Run
    repeated: bool


def benchmark(instances: list[Instance], solvers=SOLVERS, seeds=SEEDS) -> list[Cell]:
    cells = []
    for inst in instances:
        for solver in solvers:
            for seed in (seeds if TAKES_SEED[solver] else (0,)):
                a, b = run(solver, inst, seed), run(solver, inst, seed)
                same = a.status == b.status and a.objective == b.objective and a.work == b.work
                cells.append(Cell(a, same))
    return cells


def counted(r: Run, measure: str) -> float:
    return r.work[measure] * UNIT[measure][1] if r.solved else CAP[measure]


def summary(cells: list[Cell], solver: str) -> dict:
    mine = [c for c in cells if c.first.solver == solver]
    measure = MEASURES[solver][0]
    return {
        "solver": solver,
        "unit": UNIT[measure][0],
        "shift": SHIFT[measure],
        "runs": len(mine),
        "solved": sum(c.first.solved for c in mine),
        "repeat": all(c.repeated for c in mine),
        "sgm": shifted_geometric_mean([counted(c.first, measure) for c in mine], SHIFT[measure]),
        "wall_sgm": shifted_geometric_mean([c.first.wall for c in mine], WALL_SHIFT),
    }


def seed_spread(cells: list[Cell], solver: str) -> dict[str, float]:
    """Per instance: the largest over the smallest value of the solver's measure across seeds."""
    measure = MEASURES[solver][0]
    spread: dict[str, list[float]] = {}
    for c in cells:
        if c.first.solver == solver:
            spread.setdefault(c.first.instance, []).append(max(counted(c.first, measure), 1e-9))
    return {name: max(v) / min(v) for name, v in spread.items()}


def masked(seconds: float) -> str:
    """Wall-clock numbers change on every run, so a page shows the method, not the number."""
    return "<masked>"


def objectives_agree(cells: list[Cell]) -> bool:
    best: dict[str, set[int]] = {}
    for c in cells:
        if c.first.solved:
            best.setdefault(c.first.instance, set()).add(round(c.first.objective))
    return all(len(v) == 1 for v in best.values())


if __name__ == "__main__":
    instances = instance_set()
    print(f"{len(instances)} instances x seeds {SEEDS} x {len(SOLVERS)} solvers, each cell run twice")
    for inst in instances:
        model, _ = build_mathopt(inst)
        print(f"  {inst.name:<18} {len(inst.projects):>4} binaries {len(list(model.linear_constraints())):>4} rows")
    cells = benchmark(instances)
    print("every solved run found the same optimum on its instance:", objectives_agree(cells))
    print(f"\n{'solver':<7} {'unit':<14} {'shift':>6} {'runs':>5} {'solved':>7} {'repeats':>8} {'SGM':>10}   wall SGM")
    for solver in SOLVERS:
        s = summary(cells, solver)
        print(f"{s['solver']:<7} {s['unit']:<14} {s['shift']:>6g} {s['runs']:>5} {s['solved']:>7} "
              f"{'yes' if s['repeat'] else 'NO':>8} {s['sgm']:>10.2f}   {masked(s['wall_sgm'])}")
    print("\ncheapest run, in each solver's counted unit (each shift is set at about this size):")
    cheapest = {solver: min(counted(c.first, MEASURES[solver][0]) for c in cells if c.first.solver == solver)
                for solver in SOLVERS}
    print("  " + "  ".join(f"{solver} {work:,.0f}" for solver, work in cheapest.items()))
    print("\nseed spread, largest/smallest over seeds 1-3:")
    for solver in SOLVERS:
        if TAKES_SEED[solver]:
            spread = seed_spread(cells, solver)
            print(f"  {solver:<7}" + "  ".join(f"{name} {ratio:.2f}" for name, ratio in spread.items()))
