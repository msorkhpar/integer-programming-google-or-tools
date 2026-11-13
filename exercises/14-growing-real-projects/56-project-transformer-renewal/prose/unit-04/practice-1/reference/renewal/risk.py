"""Failure risk from each kind's Weibull curve, and the risk a replacement removes."""

from __future__ import annotations

import numpy as np

from .fleet import FIRST_YEAR, KINDS, Transformer, weibull_pof
from .request import Request


def pof_next(age: float, kind: str) -> float:
    """The probability that a unit of this kind, working at `age`, fails within the year."""
    return weibull_pof(age, KINDS[kind].beta, KINDS[kind].eta)


def risk_removed(t: Transformer, start: int, request: Request) -> float:
    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k.

    In each year from `start` on, the old unit's PoF at its age is replaced by a new unit's PoF at
    its age, `y - start` (lesson 7.3.4). Years before `start` keep the old unit and remove nothing.
    """
    total = 0.0
    for y in request.risk_years():
        if y >= start:
            old = pof_next(t.age + y - FIRST_YEAR, t.kind)
            new = pof_next(y - start, t.kind)
            total += (old - new) * t.cof / (1 + request.rate) ** (y - FIRST_YEAR)
    return total


def risk_table(units: list[Transformer], request: Request) -> np.ndarray:
    """Stub: the next lesson computes risk_removed for every unit and plan year with arrays."""
    return np.zeros((len(units), len(request.plan_years())))
