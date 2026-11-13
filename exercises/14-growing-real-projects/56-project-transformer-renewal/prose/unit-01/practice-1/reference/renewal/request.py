"""What the planner asks for, and what the model answers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    budget: int                 # $k for the year
    # Stubs: the next lesson gives these fields their meaning; this model ignores them.
    years: int = 1
    window: int | None = None
    rate: float = 0.07
    min_age: int = 0
    gap: float = 0.0


@dataclass(frozen=True)
class Plan:
    replace: dict[str, int]     # transformer id -> year of replacement
    value: float                # risk removed, $k: the objective
    bound: float                # no plan is worth more than this
    status: str                 # the solver's termination reason
