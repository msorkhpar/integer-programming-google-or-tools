"""Three builders of one model, checked identical and then timed, on GridCap small, medium and large.

The identity check comes first and repeats exactly; the timings come after it and change from run
to run. Each builder is timed in this process, one after another, so their ratios compare like with
like. GridCap is fictional.
"""

from __future__ import annotations

from gridcap import generate
from loop_builder import build_loops
from matrix_builder import build_matrix
from slow_builder import build_slow
from stopwatch import measure
from tables import tables_of

if __name__ == "__main__":
    measured = {}
    for size in ("small", "medium", "large"):
        portfolio = generate(size)
        tables = tables_of(portfolio)
        reference = build_loops(portfolio).export_model()
        same = {name: build(tables).export_model() == reference
                for name, build in (("slow", build_slow), ("matrix", build_matrix))}
        print(f"{size:6}: {len(reference.variables.ids):>6,} variables, {len(reference.linear_constraints.ids):>6,} rows;"
              f" identical to build_loops: slow {same['slow']}, matrix {same['matrix']}")
        slow_repeats = 1 if size == "large" else 5     # one slow build of large takes most of a minute
        measured[size] = {
            "slow": measure(lambda: build_slow(tables), repeats=slow_repeats, warmup=0),
            "loops": measure(lambda: build_loops(portfolio)),
            "matrix": measure(lambda: build_matrix(tables)),
        }
    print()
    print("measured (median seconds; speed-up over the slow builder):")
    for size, t in measured.items():
        slow = t["slow"].median
        print(f"{size:6}: slow {slow:7.3f}   loops {t['loops'].median:6.3f} ({slow / t['loops'].median:5.0f}x)"
              f"   matrix {t['matrix'].median:6.3f} ({slow / t['matrix'].median:5.0f}x)")
