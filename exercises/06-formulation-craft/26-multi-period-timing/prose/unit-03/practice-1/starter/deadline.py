from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]          # the years it may start in


def start_variables(model: mathopt.Model, projects: list[Project], integer: bool = True) -> dict:
    return {(p.pid, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.pid}_{t}")
            for p in projects for t in p.starts}


def add_aggregated_deadline(model, x, bypass: Project, replacement: Project, within: int) -> None:
    """The colleague's version: equal funding, then two rows on the start years' weighted sums."""
    funded_b = sum(x[bypass.pid, s] for s in bypass.starts)
    funded_r = sum(x[replacement.pid, u] for u in replacement.starts)
    model.add_linear_constraint(funded_r == funded_b)
    year_b = sum(s * x[bypass.pid, s] for s in bypass.starts)
    year_r = sum(u * x[replacement.pid, u] for u in replacement.starts)
    model.add_linear_constraint(year_r >= year_b)
    model.add_linear_constraint(year_r <= year_b + within * funded_b)


def add_deadline_rows(model, x, bypass: Project, replacement: Project, within: int) -> None:
    """The replacement starts in the bypass's start year or up to `within` years later, and only then."""
    # TODO: your rows, year by year.
    return None


if __name__ == "__main__":
    bypass, replacement = Project("BY", (2027, 2028, 2029)), Project("RP", (2027, 2028, 2029, 2030))
    model = mathopt.Model()
    x = start_variables(model, [bypass, replacement])
    add_deadline_rows(model, x, bypass, replacement, 1)
    print(len(list(model.linear_constraints())), "rows")
