"""A rolling horizon. Stub: the next lesson writes it; until then it plans nothing."""

from __future__ import annotations

from .fleet import Transformer
from .request import Plan, Request


def rolling(fleet: list[Transformer], request: Request, window: int = 3, keep: int = 1) -> Plan:
    return Plan({}, 0.0, 0.0, "NOT_SOLVED")
