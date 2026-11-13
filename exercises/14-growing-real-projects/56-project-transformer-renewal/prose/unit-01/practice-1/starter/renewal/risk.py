"""Failure risk from each kind's Weibull curve, and the risk a replacement removes.

Stub: the next lesson writes both functions. Until then they return 0.
"""

from __future__ import annotations

from .fleet import Transformer
from .request import Request


def pof_next(age: float, kind: str) -> float:
    """The probability that a unit of this kind, working at `age`, fails within the year."""
    return 0.0


def risk_removed(t: Transformer, start: int, request: Request) -> float:
    """The coefficient of x[i, start]: failure cost avoided over the risk window, discounted, $k."""
    return 0.0
