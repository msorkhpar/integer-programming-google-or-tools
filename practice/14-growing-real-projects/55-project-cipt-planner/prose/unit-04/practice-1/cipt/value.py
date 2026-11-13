"""What a start is worth. Stub: lesson 14.2.4 writes it; until then every start is worth nothing."""

from __future__ import annotations

from .data import Project, Request


def annual_pof(beta: float, eta: float, age: float) -> float:
    """The chance an asset of this age fails within the next year. Stub."""
    return 0.0


def risk_reduction(request: Request, project: Project, start: int) -> float:
    """Risk removed by a start in `start`. Stub."""
    return 0.0


def annual_risk(request: Request, project: Project, year: int) -> float:
    """Returns the expected failure cost, in $k, of the project's asset in a calendar year if nothing is done: the consequence of failure times the PoF at the asset's age in that year. The export's age is the asset's age in the plan's first year, so in year y the age is age + y - first year."""
    return 0.0


def coefficients(request: Request) -> dict[tuple[str, int], tuple[int, float]]:
    """Returns, for every project and start year the model has a variable for, the pair (NPV of that start, risk reduction of that start)."""
    return {}
