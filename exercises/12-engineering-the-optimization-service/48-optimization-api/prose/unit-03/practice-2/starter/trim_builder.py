from __future__ import annotations

import math  # noqa: F401
from typing import Literal

from pydantic import BaseModel, Field


class MonthHours(BaseModel):
    month: int = Field(ge=1, le=12)
    crew_hours: int = Field(ge=0)
    capacity: int = Field(ge=0)


class TrimResult(BaseModel):
    status: Literal["optimal", "time_limit", "infeasible", "failed"]
    message: str
    value: float | None
    bound: float | None
    gap: float | None = Field(ge=0)
    circuits: list[str]
    hours_by_month: list[MonthHours]


def build_result(status: str, message: str, value: float | None, bound: float, chosen: list[str],
                 work: dict[str, tuple[int, int]], capacity: dict[int, int]) -> TrimResult:
    """The result of a finished trim job.

    `value` is the plan's value, or None when the job has no plan; `bound` is the solver's best bound,
    which may be infinite; `chosen` the circuits trimmed; `work[circuit] = (month, crew_hours)`;
    `capacity[month]` the crew hours available that month.
    """
    # TODO: the gap, a JSON-safe bound, one row per month of capacity, and the sorted circuits.
    return TrimResult(status=status, message=message, value=value, bound=None, gap=None,
                      circuits=[], hours_by_month=[])

if __name__ == "__main__":
    print(build_result("time_limit", "No plan found within the 30 s limit.", None, math.inf, [], {}, {3: 160})
          .model_dump_json())
