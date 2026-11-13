"""The model: a start-year decision per project and year, and the rows the rules add."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from .data import Request
from .rules import RULES
from .value import coefficients


@dataclass
class Built:
    """A built model and the handles the rest of the planner needs to read it."""

    request: Request
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    rows: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)
    npv: mathopt.LinearSum | None = None       # the plan's NPV, $k
    risk: mathopt.LinearSum | None = None      # the risk the plan removes, $k

    def add(self, name: str, row) -> None:
        """Add one named row; the name is how reports and diagnostics refer to it."""
        self.rows[name] = self.model.add_linear_constraint(row, name=name)

    def started(self, pid: str) -> mathopt.LinearSum:
        """1 if project `pid` starts in some year of its window, else 0."""
        return mathopt.fast_sum(v for (p, _), v in self.x.items() if p == pid)

    def started_by(self, pid: str, year: int) -> mathopt.LinearSum:
        """1 if project `pid` starts in `year` or earlier, else 0."""
        return mathopt.fast_sum(v for (p, t), v in self.x.items() if p == pid and t <= year)

    def spend_by_year(self) -> dict[int, mathopt.LinearSum]:
        """Each year's spend as an expression, with every project's cost spread over its years of work."""
        terms: dict[int, list] = {y: [] for y in self.request.years}
        for (pid, t), v in self.x.items():
            for year, amount in self.request.project(pid).spend(t).items():
                terms[year].append(amount * v)
        return {y: mathopt.fast_sum(ts) for y, ts in terms.items()}


def build(request: Request) -> Built:
    model = mathopt.Model(name=request.name)
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in request.projects for t in request.starts(p)}
    built = Built(request, model, x)
    for rule in RULES:
        rule(built)
    value = coefficients(request)
    built.npv = mathopt.fast_sum(value[key][0] * v for key, v in x.items())
    built.risk = mathopt.fast_sum(value[key][1] * v for key, v in x.items())
    model.maximize(built.npv if request.objective == "npv" else built.risk)
    return built
