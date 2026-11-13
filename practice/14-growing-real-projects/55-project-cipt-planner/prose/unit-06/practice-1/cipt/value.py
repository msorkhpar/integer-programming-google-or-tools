"""What a start is worth: NPV by start year, and the failure risk the work removes.

NPV comes from finance, one figure per start year (lesson 7.2.4). Risk is computed here from the
asset's Weibull curve (lesson 7.3.1) and its consequence of failure (lesson 7.3.3): the work removes
the asset's yearly risk, PoF x CoF, from the year after the work ends to the plan's last year
(lesson 7.3.4).
"""

from __future__ import annotations

import math

from .data import Project, Request


def annual_pof(beta: float, eta: float, age: float) -> float:
    """The chance an asset of this age fails within the next year, given that it has not failed yet."""
    return 1.0 - math.exp((age / eta) ** beta - ((age + 1) / eta) ** beta)


def annual_risk(request: Request, project: Project, year: int) -> float:
    """Expected failure cost of the project's asset in `year` if nothing is done ($k)."""
    a = project.asset
    return a.cof * annual_pof(a.weibull_beta, a.weibull_eta, a.age + year - request.years[0])


def risk_reduction(request: Request, project: Project, start: int) -> float:
    """Risk removed by a start in `start`: every year after the work ends, to the plan's last year."""
    return sum(annual_risk(request, project, y) for y in range(start + project.duration, request.years[-1] + 1))


def coefficients(request: Request) -> dict[tuple[str, int], tuple[int, float]]:
    """(npv, risk reduction) for every project and start year the model has a variable for."""
    return {(p.project_id, t): (p.npv[t], risk_reduction(request, p, t))
            for p in request.projects for t in request.starts(p)}
