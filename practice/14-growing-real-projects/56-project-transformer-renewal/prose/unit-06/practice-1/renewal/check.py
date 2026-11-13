"""Every rule of the request, checked on a finished plan. Stub: the next lesson writes the checks."""

from __future__ import annotations

from .fleet import Transformer
from .request import Request


def violations(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> list[str]:
    """One line per broken rule; an empty list means the plan keeps every rule."""
    return []
