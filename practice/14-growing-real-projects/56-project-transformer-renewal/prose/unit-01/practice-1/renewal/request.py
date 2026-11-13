"""What the planner asks for, and what the model answers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    budget: int                 # $k for the year


@dataclass(frozen=True)
class Plan:
    replace: dict[str, int]     # transformer id -> year of replacement
    value: float                # risk removed, $k: the objective
    bound: float                # no plan is worth more than this
    status: str                 # the solver's termination reason
