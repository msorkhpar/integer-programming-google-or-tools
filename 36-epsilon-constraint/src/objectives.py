"""GridCap's two objectives, NPV and risk removed, on the start-year model of lessons 6.4.1-6.4.2.

The risk coefficients follow lesson 7.3.4 (module 32, `asset_curves.py` and `risk_model.py`), copied
here so this module runs on its own. The one change: `build` sets no objective. It returns the two
objective expressions, and each lesson decides how to combine them.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

WINDOW = 10        # years over which a project's risk reduction is counted, from the plan's first year
#: The share of its age an asset keeps after each kind of work (the convention of lesson 1.1.2).
AGE_AFTER = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
             "clear": 0.5, "widen": 0.5}


def yearly_risk(age: float, beta: float, eta: float, cof: float) -> float:
    """Expected failure cost in the coming year, $k: CoF times the expected failures at this age."""
    return cof * (((age + 1) / eta) ** beta - (age / eta) ** beta)


def risk_reduction(asset, window, start: int, duration: int, keep: float, rate: float) -> float:
    """Discounted risk removed over `window` by work that starts in `start` (lesson 7.3.4)."""
    first, done = window[0], start + duration
    total = 0.0
    for y in window:
        before = asset.age + (y - first)
        after = before if y < done else keep * (asset.age + (done - first)) + (y - done)
        cut = (yearly_risk(before, asset.weibull_beta, asset.weibull_eta, asset.cof)
               - yearly_risk(after, asset.weibull_beta, asset.weibull_eta, asset.cof))
        total += cut / (1 + rate) ** (y - first)
    return total


def risk_coefficients(portfolio: Portfolio) -> dict[tuple[str, int], float]:
    """rr[i, s]: discounted risk removed over the window if project i starts in year s, $k."""
    window = tuple(range(portfolio.years[0], portfolio.years[0] + WINDOW))
    return {(p.project_id, s): risk_reduction(portfolio.asset(p.asset_id), window, s, p.duration,
                                              AGE_AFTER[p.intervention], portfolio.discount_rate)
            for p in portfolio.projects for s in p.starts()}


@dataclass
class TwoObjectives:
    """The start-year model with every rule and no objective, plus its two objective expressions."""
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    npv: mathopt.LinearExpression     # $k, integer coefficients
    risk: mathopt.LinearExpression    # $k removed, discounted, real coefficients
    npv_of: dict[tuple[str, int], int]
    rr_of: dict[tuple[str, int], float]

    def plan(self, values) -> dict[str, int]:
        """Project id -> start year, from a solution's variable values."""
        return {pid: t for (pid, t), v in self.x.items() if values[v] > 0.5}


def build(portfolio: Portfolio) -> TwoObjectives:
    """Lesson 6.4.2's rows: once, must, alt, after and budget. No objective is set."""
    model = mathopt.Model(name=f"{portfolio.name} NPV and risk")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str):
        return mathopt.LinearExpression() + sum(x[pid, t] for t in by_id[pid].starts())

    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= mathopt.LinearExpression() + sum(x[parent.project_id, s] for s in parent.starts()
                                                        if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    npv_of = {(p.project_id, s): p.npv[s] for p in portfolio.projects for s in p.starts()}
    rr_of = risk_coefficients(portfolio)
    npv = mathopt.LinearExpression() + sum(npv_of[k] * v for k, v in x.items())
    risk = mathopt.LinearExpression() + sum(rr_of[k] * v for k, v in x.items())
    return TwoObjectives(model, x, npv, risk, npv_of, rr_of)
