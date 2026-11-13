"""The planner as an HTTP service: POST a season, get its plan's record and a number; GET it back later.

The request is checked at the edge by pydantic models, so the planner only ever sees a well-formed
season. An infeasible season is an answer (200, with the explanation), not an error.
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from vegcrew.data import Override, season_from_dict
from vegcrew.planner import check_overrides, make_plan
from vegcrew.record import plan_record
from vegcrew.store import Store

Span = tuple[int, int]


class CircuitIn(BaseModel):
    id: str
    region: str
    miles: int = Field(gt=0)
    cost: int = Field(ge=0)
    risk: int = Field(ge=0)
    weeks: int = Field(ge=1)
    growth: float = Field(ge=0)
    windows: list[Span] = []
    must: bool = False


class SeasonIn(BaseModel):
    name: str = "season"
    budget: int = Field(ge=0)
    crews: int = Field(ge=1, le=50)
    months: int = Field(ge=1, le=12)
    crew_off: dict[str, list[Span]] = {}
    circuits: list[CircuitIn] = Field(min_length=1)


class OverrideIn(BaseModel):
    kind: Literal["pin", "skip", "force"]
    cid: str
    crew: str | None = None
    start: int | None = None
    reason: str = ""


class PlanRequest(BaseModel):
    season: SeasonIn
    overrides: list[OverrideIn] = []


def create_app(db: str = ":memory:") -> FastAPI:
    app = FastAPI(title="Vegetation crew planner")
    store = Store(db)

    @app.post("/plans")
    def post_plan(request: PlanRequest) -> dict:          # def, not async def: the solve blocks
        raw = request.season.model_dump()
        season = season_from_dict(raw)
        overrides = tuple(Override(**o.model_dump()) for o in request.overrides)
        problems = check_overrides(season, overrides)
        if problems:
            raise HTTPException(status_code=422, detail=problems)
        record = plan_record(raw, make_plan(season, overrides), overrides)
        return {"id": store.save(record), "record": record}

    @app.get("/plans/{plan_id}")
    def get_plan(plan_id: int) -> dict:
        record = store.get(plan_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"no plan {plan_id}")
        return {"id": plan_id, "record": record}

    return app
