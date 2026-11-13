"""Lesson 12.4.1's planning API: one FastAPI app that validates a request, solves, and answers.

GridCap is fictional. The solve runs inside the request, which is fine for the tiny and small
portfolios (well under a second each) and is exactly what lesson 12.4.2 replaces with jobs.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from ortools.math_opt.python import mathopt
from pydantic import BaseModel, ConfigDict, Field

from gridcap import generate
from plan_model import build, spend_of, starts_of

app = FastAPI(title="GridCap planning API", version="0.1.0")

Money = Annotated[int, Field(ge=0, description="$k")]


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolio: Literal["tiny", "small"]
    budget: dict[int, Money] = Field(default_factory=dict, description="year -> budget; missing years keep the portfolio's")
    time_limit_s: float = Field(default=10.0, gt=0, le=60)


class PlanResponse(BaseModel):
    status: str
    npv: float | None
    starts: dict[str, int]
    spend: dict[int, int]


class PortfolioInfo(BaseModel):
    name: str
    projects: int
    years: list[int]
    budget: dict[int, int]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/portfolios/{name}", responses={404: {"description": "No portfolio has that name"}})
def portfolio_info(name: str) -> PortfolioInfo:
    if name not in ("tiny", "small"):
        raise HTTPException(status_code=404, detail=f"no portfolio named {name!r}")
    pf = generate(name)
    return PortfolioInfo(name=name, projects=len(pf.projects), years=list(pf.years), budget=dict(pf.budget))


@app.post("/plans")
def make_plan(request: PlanRequest) -> PlanResponse:
    pf = generate(request.portfolio)
    unknown = sorted(set(request.budget) - set(pf.years))
    if unknown:
        raise HTTPException(status_code=422, detail=f"budget years {unknown} are outside the plan's years {list(pf.years)}")
    pm = build(pf, {**pf.budget, **request.budget})
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=request.time_limit_s))
    result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS, params=params)
    if not result.has_primal_feasible_solution():
        return PlanResponse(status=result.termination.reason.name.lower(), npv=None, starts={}, spend={})
    starts = starts_of(pm, result)
    return PlanResponse(status=result.termination.reason.name.lower(), npv=result.objective_value(),
                        starts=starts, spend=spend_of(pf, starts))
