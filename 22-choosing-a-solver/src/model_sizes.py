"""GridCap's model sizes against the free size-limited licenses of three commercial solvers (lesson 5.4.3).

The limits are the vendors' own published terms, as of the pages opened on 2026-11-11; terms change,
so the date travels with them. Nothing here runs a commercial solver: a size is a count of the
model's variables and linear constraints, which any MathOpt model reports.
"""

from __future__ import annotations

from dataclasses import dataclass

from gridcap import generate

from instances import Instance, build_mathopt

AS_OF = "2026-11-11"


@dataclass(frozen=True)
class Limit:
    name: str
    max_vars: int | None              # None: no separate cap on this count
    max_rows: int | None
    max_sum: int | None               # a cap on variables + rows together

    def fits(self, n_vars: int, n_rows: int) -> bool:
        return ((self.max_vars is None or n_vars <= self.max_vars)
                and (self.max_rows is None or n_rows <= self.max_rows)
                and (self.max_sum is None or n_vars + n_rows <= self.max_sum))


LIMITS = (
    Limit("Gurobi pip license", 2_000, 2_000, None),        # linear models; 200 variables with quadratic terms
    Limit("CPLEX Community Edition", 1_000, 1_000, None),
    Limit("Xpress Community License", None, None, 5_000),   # rows + columns, linear and MIP models
)


def selection_size(size: str) -> tuple[int, int]:
    pf = generate(size)
    model, _ = build_mathopt(Instance(size, pf.projects, pf.years, dict(pf.budget)))
    return len(list(model.variables())), len(list(model.linear_constraints()))


def timing_size(size: str) -> tuple[int, int]:
    """Lesson 6.4.2's model: x[i,t] per allowed start; once/must, alt, after_{c,t} and budget rows."""
    pf = generate(size)
    n_vars = sum(len(p.starts()) for p in pf.projects)
    groups = {p.alt_group for p in pf.projects if p.alt_group}
    after = sum(len(p.starts()) for p in pf.projects if p.parent)
    return n_vars, len(pf.projects) + len(groups) + after + len(pf.years)


print(f"free size limits as published (pages opened {AS_OF}):")
for lim in LIMITS:
    parts = [f"{lim.max_vars:,} variables" if lim.max_vars else "",
             f"{lim.max_rows:,} constraints" if lim.max_rows else "",
             f"{lim.max_sum:,} variables + constraints" if lim.max_sum else ""]
    print(f"  {lim.name:<25} {', '.join(p for p in parts if p)}")

print(f"\n{'model':<17} {'variables':>10} {'rows':>7}   " + "   ".join(f"{lim.name.split()[0]:<7}" for lim in LIMITS))
for size in ("tiny", "small", "medium", "large"):
    for label, count in (("selection", selection_size), ("timing", timing_size)):
        n_vars, n_rows = count(size)
        verdict = "   ".join(f"{'fits' if lim.fits(n_vars, n_rows) else 'too big':<7}" for lim in LIMITS)
        print(f"{size + ' ' + label:<17} {n_vars:>10,} {n_rows:>7,}   {verdict}")
