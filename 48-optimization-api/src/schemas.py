"""Lesson 12.4.3's result schema: what a finished job returns, in a shape a planner tool can read.

GridCap is fictional. Money is in $k. Every number a planner reads is written from the data and the
job's outcome, never typed (lesson 9.3.4).
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from jobs import JobRequest, Outcome, portfolio
from plan_model import spend_of

#: The solver settings every job runs with; they are part of what the snapshot id covers.
SETTINGS = {"solver": "HIGHS", "relative_gap_tolerance": 0.0}


class ProjectStart(BaseModel):
    project_id: str
    start_year: int
    program: str
    region: str
    capex: int = Field(description="total cost over the project's years of work, $k")
    npv: int = Field(description="NPV of the project at this start year, $k")


class YearSpend(BaseModel):
    year: int
    spend: int = Field(description="what the plan spends this year, $k")
    budget: int = Field(description="the budget the job ran with, $k")
    headroom: int = Field(description="budget minus spend, $k")


class PlanResult(BaseModel):
    schema_version: Literal["1.0"] = Field(default="1.0", description="changes only when a field changes meaning")
    job_id: str = Field(description="the id POST /jobs returned")
    snapshot: str = Field(description="sha256 of the request, the portfolio and the solver settings")
    status: Literal["optimal", "time_limit", "infeasible", "failed"] = Field(description="how the solve ended")
    message: str = Field(description="one paragraph for the planner, written from the fields below")
    npv: float | None = Field(description="NPV of the plan, $k; null when there is no plan")
    bound: float | None = Field(description="no plan is worth more than this, $k; null when unknown")
    gap: float | None = Field(ge=0, description="max(0, bound - npv) / max(|npv|, 1); null when there is no plan")
    plan: list[ProjectStart] = Field(description="one row per funded project; empty when there is no plan")
    spend_by_year: list[YearSpend] = Field(description="one row per year; empty when there is no plan")

    @model_validator(mode="after")
    def consistent(self) -> "PlanResult":
        has_plan = self.npv is not None
        if self.status == "optimal" and not has_plan:
            raise ValueError("an optimal result must carry its plan's npv")
        if self.status in ("infeasible", "failed") and (has_plan or self.plan):
            raise ValueError(f"a result with status {self.status} has no plan")
        if (self.gap is None) != (self.npv is None or self.bound is None):
            raise ValueError("gap is given exactly when both npv and bound are")
        return self


def snapshot(request: JobRequest) -> str:
    """sha256 of everything the job's answer depends on (lesson 7.1.3's snapshot id)."""
    inputs = {"request": request.model_dump(mode="json"), "portfolio": portfolio(request.portfolio).content_hash(),
              "settings": SETTINGS}
    return hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def to_result(job_id: str, request: JobRequest, outcome: Outcome) -> PlanResult:
    pf = portfolio(request.portfolio)
    budget = {**pf.budget, **request.budget}
    plan = [ProjectStart(project_id=pid, start_year=t, program=pf.project(pid).program,
                         region=pf.project(pid).region, capex=pf.project(pid).capex, npv=pf.project(pid).npv[t])
            for pid, t in outcome.starts.items()]
    spend = spend_of(pf, outcome.starts) if outcome.npv is not None else {}
    years = [YearSpend(year=y, spend=spend[y], budget=budget[y], headroom=budget[y] - spend[y]) for y in spend]
    return PlanResult(job_id=job_id, snapshot=snapshot(request), status=outcome.status, message=outcome.message,
                      npv=outcome.npv, bound=outcome.bound, gap=outcome.gap, plan=plan, spend_by_year=years)
