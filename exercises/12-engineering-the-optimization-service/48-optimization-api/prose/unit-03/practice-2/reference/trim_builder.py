from __future__ import annotations

import math
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
    finite = bound if bound is not None and math.isfinite(bound) else None
    gap = None
    if value is not None and finite is not None:
        gap = max(0.0, finite - value) / max(abs(value), 1.0)
    hours = {m: 0 for m in capacity}
    for circuit in chosen:
        month, crew_hours = work[circuit]
        hours[month] += crew_hours
    rows = [MonthHours(month=m, crew_hours=hours[m], capacity=capacity[m]) for m in sorted(capacity)]
    return TrimResult(status=status, message=message, value=value, bound=finite, gap=gap,
                      circuits=sorted(chosen), hours_by_month=rows if value is not None else [])


if __name__ == "__main__":
    print(build_result("time_limit", "No plan found within the 30 s limit.", None, math.inf, [], {}, {3: 160})
          .model_dump_json())
