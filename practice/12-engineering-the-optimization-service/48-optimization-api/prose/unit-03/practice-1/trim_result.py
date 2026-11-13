from __future__ import annotations

from pydantic import BaseModel, Field, model_validator  # noqa: F401


class MonthHours(BaseModel):
    month: int
    crew_hours: int
    capacity: int


class TrimResult(BaseModel):
    """What the trim service returns for a finished job."""

    # TODO: give each field its rules, and add one validator that refuses a result whose fields disagree.
    status: str
    message: str
    value: float | None          # outage-minutes avoided per year; None when there is no plan
    bound: float | None          # no plan avoids more; None when unknown
    gap: float | None
    circuits: list[str]
    hours_by_month: list[MonthHours]


if __name__ == "__main__":
    print(TrimResult(status="infeasible", message="No plan.", value=None, bound=None, gap=None,
                     circuits=[], hours_by_month=[]).model_dump_json())
