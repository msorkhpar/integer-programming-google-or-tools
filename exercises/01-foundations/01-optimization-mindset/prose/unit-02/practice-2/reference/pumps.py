from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations

#: The share of its age an asset keeps after each kind of work.
AGE_AFTER = {"replace": 0.0, "repair": 0.5}


@dataclass(frozen=True)
class Asset:
    age: float
    cof: float      # what one failure costs, $k
    beta: float     # Weibull shape
    eta: float      # Weibull scale, years


@dataclass(frozen=True)
class Project:
    pid: str
    asset: str
    work: str       # a key of AGE_AFTER
    cost: int
    must_do: bool = False


def pof_next(age: float, beta: float, eta: float) -> float:
    """Probability of failing in the coming year, given the asset works at `age`."""
    def failed_by(t: float) -> float:
        return 1 - math.exp(-((t / eta) ** beta))
    return (failed_by(age + 1) - failed_by(age)) / (1 - failed_by(age))


def allowed(projects: list[Project], plan: frozenset[str], budget: int) -> bool:
    """The rules: within budget, every must-do funded, at most one project per asset."""
    chosen = [p for p in projects if p.pid in plan]
    assets = [p.asset for p in chosen]
    return (sum(p.cost for p in chosen) <= budget
            and all(p.pid in plan for p in projects if p.must_do)
            and len(assets) == len(set(assets)))


def risk_avoided(project: Project, assets: dict[str, Asset]) -> float:
    """a_i: the yearly failure cost the project's work removes, in $k."""
    a = assets[project.asset]
    kept = AGE_AFTER[project.work] * a.age
    return a.cof * (pof_next(a.age, a.beta, a.eta) - pof_next(kept, a.beta, a.eta))


def most_risk_removed(projects: list[Project], assets: dict[str, Asset],
                      budget: int) -> tuple[float, frozenset[str]]:
    """The allowed plan with the largest total risk avoided, and that total."""
    best: tuple[float, frozenset[str]] = (-1.0, frozenset())
    for k in range(len(projects) + 1):
        for combo in combinations(projects, k):
            plan = frozenset(p.pid for p in combo)
            if allowed(projects, plan, budget):
                total = sum(risk_avoided(p, assets) for p in combo)
                if total > best[0]:
                    best = (total, plan)
    return best


if __name__ == "__main__":
    pumps = {"K1": Asset(age=30, cof=900, beta=3.0, eta=40)}
    work = [Project("W1", "K1", "replace", 400), Project("W2", "K1", "repair", 80)]
    print([round(risk_avoided(p, pumps), 1) for p in work], most_risk_removed(work, pumps, 300))
