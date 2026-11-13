"""Failure risk from each kind's Weibull curve, and the risk a replacement removes, under a scenario
for the curves (the base curves unless one is given)."""

from __future__ import annotations

import numpy as np

from .fleet import FIRST_YEAR, KINDS, Transformer, weibull_pof
from .request import BASE, Request, Scenario


def curve(kind: str, scenario: Scenario = BASE) -> tuple[float, float]:
    """(beta, eta) of a kind's failure curve under a scenario."""
    return KINDS[kind].beta * scenario.beta, KINDS[kind].eta * scenario.eta


def pof_next(age: float, kind: str, scenario: Scenario = BASE) -> float:
    """The probability that a unit of this kind, working at `age`, fails within the year."""
    return weibull_pof(age, *curve(kind, scenario))


def risk_removed(t: Transformer, start: int, request: Request, scenario: Scenario = BASE) -> float:
    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k.

    In each year from `start` on, the old unit's PoF at its age is replaced by a new unit's PoF at
    its age, `y - start` (lesson 7.3.4). Years before `start` keep the old unit and remove nothing.
    """
    total = 0.0
    for y in request.risk_years():
        if y >= start:
            old = pof_next(t.age + y - FIRST_YEAR, t.kind, scenario)
            new = pof_next(y - start, t.kind, scenario)
            total += (old - new) * t.cof / (1 + request.rate) ** (y - FIRST_YEAR)
    return total


def risk_table(units: list[Transformer], request: Request, scenario: Scenario = BASE) -> np.ndarray:
    """risk_removed for every unit (rows) and plan year (columns) at once, with arrays.

    rr[i, j] = cof_i * sum over risk years k >= j of (old_pof[i, k] - new_pof[k - j]) / (1 + r)^k,
    where k counts years from FIRST_YEAR. A new unit's PoF depends only on its kind and age, so it
    is computed once per kind.
    """
    years, window = len(request.plan_years()), len(request.risk_years())
    k = np.arange(window)
    discount = (1 + request.rate) ** -k
    after = k[None, :] >= np.arange(years)[:, None]                 # [j, k]: year k is on or after start j
    table = np.zeros((len(units), years))
    for kind in KINDS:
        rows = [i for i, t in enumerate(units) if t.kind == kind]
        if not rows:
            continue
        beta, eta = curve(kind, scenario)
        age = np.array([units[i].age for i in rows], dtype=float)
        cof = np.array([units[i].cof for i in rows], dtype=float)
        old = _pof(age[:, None] + k[None, :], beta, eta)                                         # [i, k]
        new = np.where(after, _pof(np.maximum(k[None, :] - np.arange(years)[:, None], 0),
                                   beta, eta), 0.0)                                      # [j, k]
        table[rows] = cof[:, None] * ((old * discount) @ after.T - (new * discount).sum(axis=1)[None, :])
    return table


def _pof(age: np.ndarray, beta: float, eta: float) -> np.ndarray:
    return 1 - np.exp((age / eta) ** beta - ((age + 1) / eta) ** beta)


def evaluate(fleet: list[Transformer], request: Request, replace: dict[str, int], scenario: Scenario) -> float:
    """What a finished plan removes if `scenario` is how the fleet really fails, $k."""
    by_id = {t.tid: t for t in fleet}
    return sum(risk_removed(by_id[tid], y, request, scenario) for tid, y in replace.items())
