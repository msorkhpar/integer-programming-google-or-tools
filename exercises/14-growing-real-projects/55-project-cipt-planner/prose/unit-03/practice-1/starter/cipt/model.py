"""The model: a start-year decision per project and year, one budget row per year."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from .data import Request


@dataclass
class Built:
    """A built model and the handles the rest of the planner needs to read it."""

    request: Request
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    rows: dict[str, mathopt.LinearConstraint]

    def started(self, pid: str) -> mathopt.LinearSum:
        """1 if project `pid` starts in some year of its window, else 0."""
        return mathopt.fast_sum(v for (p, _), v in self.x.items() if p == pid)


def spend_by_year(request: Request, x: dict) -> dict[int, mathopt.LinearSum]:
    """Each year's spend as an expression, with every project's cost spread over its years of work."""
    terms: dict[int, list] = {y: [] for y in request.years}
    for p in request.projects:
        for t in request.starts(p):
            for year, amount in p.spend(t).items():
                terms[year].append(amount * x[p.project_id, t])
    return {y: mathopt.fast_sum(ts) for y, ts in terms.items()}


def build(request: Request) -> Built:
    model = mathopt.Model(name=request.name)
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in request.projects for t in request.starts(p)}
    built = Built(request, model, x, {})
    for p in request.projects:                                            # (once_i)
        name = f"once_{p.project_id}"
        built.rows[name] = model.add_linear_constraint(built.started(p.project_id) <= 1, name=name)
    for y, spend in spend_by_year(request, x).items():                    # (budget_y)
        name = f"budget_{y}"
        built.rows[name] = model.add_linear_constraint(spend <= request.budget[y], name=name)
    model.maximize(mathopt.fast_sum(request.project(pid).value * v for (pid, _), v in x.items()))
    return built
