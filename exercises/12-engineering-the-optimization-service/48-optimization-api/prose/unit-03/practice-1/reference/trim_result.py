from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class MonthHours(BaseModel):
    month: int = Field(ge=1, le=12)
    crew_hours: int = Field(ge=0)
    capacity: int = Field(ge=0)


class TrimResult(BaseModel):
    """What the trim service returns for a finished job."""

    status: Literal["optimal", "time_limit", "infeasible", "failed"]
    message: str = Field(min_length=1)
    value: float | None          # outage-minutes avoided per year; None when there is no plan
    bound: float | None          # no plan avoids more; None when unknown
    gap: float | None = Field(ge=0)
    circuits: list[str]
    hours_by_month: list[MonthHours]

    @model_validator(mode="after")
    def tells_one_story(self) -> "TrimResult":
        if self.status == "optimal" and self.value is None:
            raise ValueError("an optimal result carries its value")
        if self.status in ("infeasible", "failed") and (self.value is not None or self.circuits):
            raise ValueError("a result without a plan lists no circuits and no value")
        if (self.gap is None) != (self.value is None or self.bound is None):
            raise ValueError("gap is given exactly when value and bound are")
        months = [m.month for m in self.hours_by_month]
        if months != sorted(set(months)):
            raise ValueError("months are listed once each, in order")
        if any(m.crew_hours > m.capacity for m in self.hours_by_month):
            raise ValueError("a month's crew hours exceed its capacity")
        return self


if __name__ == "__main__":
    print(TrimResult(status="infeasible", message="No plan.", value=None, bound=None, gap=None,
                     circuits=[], hours_by_month=[]).model_dump_json())
