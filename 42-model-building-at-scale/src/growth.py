"""How build time grows with the portfolio: three builders on the first n projects of GridCap large.

Doubling n doubles the work of a builder whose time is linear in n and quadruples it for one whose
time is quadratic. The growth exponent between two sizes is log(t2 / t1) / log(n2 / n1). The times
are wall-clock samples and change between runs; the exponents change much less. GridCap is fictional.
"""

from __future__ import annotations

import math
from dataclasses import replace

from gridcap import Portfolio, generate
from loop_builder import build_loops
from matrix_builder import build_matrix
from slow_builder import build_slow
from stopwatch import measure
from tables import Tables, tables_of

SIZES = (1_250, 2_500, 5_000, 10_000)


def first_projects(portfolio: Portfolio, n: int) -> Portfolio:
    """The first n projects. A child's parent is the project just before it, so none is cut off."""
    return replace(portfolio, name=f"{portfolio.name} first {n}", projects=portfolio.projects[:n])


def first_rows(t: Tables, n: int) -> Tables:
    keep = set(t.projects["project_id"].iloc[:n])
    return Tables(f"{t.name} first {n}", t.projects.iloc[:n].reset_index(drop=True),
                  t.starts[t.starts["project_id"].isin(keep)].reset_index(drop=True),
                  t.costs[t.costs["project_id"].isin(keep)].reset_index(drop=True), t.budget)


def exponent(sizes: tuple[int, ...], seconds: list[float]) -> float:
    """The slope of log(time) against log(n), fitted by least squares over every size."""
    xs, ys = [math.log(n) for n in sizes], [math.log(s) for s in seconds]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def rows_scanned(t: Tables) -> int:
    """Table rows compared by build_slow's boolean masks: a count of work that no clock can blur."""
    groups = t.projects.loc[t.projects["alt_group"] != "", "alt_group"]
    children = int((t.projects["parent"] != "").sum())
    starts_of_calls = len(t.projects) + len(groups) + 2 * children
    return (starts_of_calls * len(t.starts)                   # starts_of: one mask per call
            + len(t.starts) * len(t.costs)                    # one cost-profile mask per start row
            + (groups.nunique() + 2) * len(t.projects))       # the group and child filters


if __name__ == "__main__":
    large = generate("large")
    tables = tables_of(large)
    times: dict[str, list[float]] = {"slow": [], "loops": [], "matrix": []}
    scanned = []
    for n in SIZES:
        p, t = first_projects(large, n), first_rows(tables, n)
        scanned.append(rows_scanned(t))
        growth = f" ({scanned[-1] / scanned[-2]:.2f}x the size before)" if len(scanned) > 1 else ""
        print(f"n={n:>6,}: {len(t.starts):>6,} start rows, {len(t.costs):>6,} cost rows; "
              f"slow builder's masks compare {scanned[-1]:,} rows{growth}")
        repeats = 3 if n <= 2_500 else 1          # the slow builder takes most of a minute at 10,000
        times["slow"].append(measure(lambda: build_slow(t), repeats=repeats, warmup=0).median)
        times["loops"].append(measure(lambda: build_loops(p), repeats=3).median)
        times["matrix"].append(measure(lambda: build_matrix(t), repeats=3).median)
    print()
    print("measured (median seconds at n = " + ", ".join(f"{n:,}" for n in SIZES) + "; fitted exponent):")
    for name, ts in times.items():
        cells = "  ".join(f"{s:7.3f}" for s in ts)
        print(f"{name:6} {cells}   exponent {exponent(SIZES, ts):.1f}")
