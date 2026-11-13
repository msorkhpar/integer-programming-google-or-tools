"""A solver recommendation for GridCap's planning service, written from requirements and the harness's evidence (lesson 5.4.4).

Hard requirements filter; measured evidence ranks what is left; every number in the memo is one the
harness can repeat. Wall-clock time enters only as a coarse, masked check. GridCap is fictional.
"""

from __future__ import annotations

from harness import SOLVERS, benchmark, objectives_agree, seed_spread, summary
from instances import instance_set

#: What each candidate offers, from the runner (lessons 4.1.2, 4.2.3, 5.4.1) and the vendors' pages.
FACTS = {
    "HiGHS":  {"in_mathopt": True, "exact_continuous": True, "offline_license": True, "license": "MIT"},
    "SCIP":   {"in_mathopt": True, "exact_continuous": True, "offline_license": True, "license": "Apache-2.0"},
    "CP-SAT": {"in_mathopt": True, "exact_continuous": False, "offline_license": True, "license": "Apache-2.0"},
    "CBC":    {"in_mathopt": False, "exact_continuous": True, "offline_license": True, "license": "EPL-2.0"},
    "Gurobi": {"in_mathopt": False, "exact_continuous": True, "offline_license": False, "license": "commercial"},
}
REQUIREMENTS = (
    ("in_mathopt", "one model code, solver chosen by SolverType (no second model to keep in step)"),
    ("exact_continuous", "continuous variables solved exactly (the timing model's carry-over r_y)"),
    ("offline_license", "runs in a batch container with no internet and no license server"),
)
WALL_FACTOR = 3.0
AS_OF = "2026-11-11"


def main() -> None:
    cells = benchmark(instance_set())
    print("RECOMMENDATION: MILP solver for the GridCap planning service")
    print("\n1. Requirements (hard; a candidate failing one is out)")
    for key, words in REQUIREMENTS:
        print(f"   - {words}")
    print("\n2. Candidates against the requirements")
    passing = []
    for name, facts in FACTS.items():
        failed = [key for key, _ in REQUIREMENTS if not facts[key]]
        print(f"   {name:<7} {'passes' if not failed else 'out: fails ' + ', '.join(failed)}")
        if not failed:
            passing.append(name)
    print(f"   not measured: CPLEX and Xpress (not in the runner). Commercial terms as of the pages opened")
    print(f"   {AS_OF}: deployment prices by quote; CPLEX development from $320.00 USD per user per month.")

    print("\n3. Evidence: 6 GridCap instances x seeds 1-3, one thread, gap target 0, each cell run twice")
    print(f"   every solver found the same optimum on every instance: {objectives_agree(cells)}")
    print(f"   {'solver':<7} {'solved':>7} {'repeats':>8} {'worst seed spread':>18}")
    for solver in SOLVERS:
        s = summary(cells, solver)
        spread = seed_spread(cells, solver)
        worst = f"{max(spread.values()):.2f}" if s["runs"] > len(spread) else "n/a (no seed)"
        print(f"   {solver:<7} {s['solved']:>3}/{s['runs']:<3} {'yes' if s['repeat'] else 'NO':>8} {worst:>18}")
    walls = [summary(cells, solver)["wall_sgm"] for solver in SOLVERS]
    close = max(walls) <= WALL_FACTOR * min(walls)
    print(f"   wall-clock SGMs within a factor of {WALL_FACTOR:g} of each other: "
          f"{'yes' if close else 'no'} (values masked: they change every run)")

    finalists = [s for s in passing if summary(cells, s)["solved"] == summary(cells, s)["runs"]
                 and summary(cells, s)["repeat"]]
    choice = min(finalists, key=lambda s: max(seed_spread(cells, s).values()))
    backup = [s for s in finalists if s != choice]
    print("\n4. Recommendation")
    print(f"   Use {choice} ({FACTS[choice]['license']}) through MathOpt as the default solver.")
    print(f"   Reason: it meets every requirement, solved and repeated every run, and its work varied least")
    print("   across seeds; " + ("speed does not separate the candidates on this set." if close
                              else "wall time differs by more than the factor: report it with date and machine."))
    for other in backup:
        print(f"   Keep {other} ({FACTS[other]['license']}) as the second solver: same model code, one enum away.")
        if other == "SCIP":
            print("   It accepts quadratic objectives and indicator constraints, which HiGHS refuses (capabilities.py showed both).")
    print("\n5. Revisit when")
    print("   - a GridCap large solve misses its gap target inside the batch window;")
    print("   - the service may call out to a license service (then price a commercial solver);")
    print("   - OR-Tools is upgraded: rerun this harness on the new pin before switching.")


if __name__ == "__main__":
    main()
