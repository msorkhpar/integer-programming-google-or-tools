from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException  # noqa: F401
from ortools.math_opt.python import mathopt  # noqa: F401
from pydantic import BaseModel, ConfigDict, Field


class Circuit(BaseModel):
    circuit_id: str
    cost: int = Field(ge=0)              # $k
    risk_reduction: float = Field(ge=0)  # expected outage-minutes avoided per year


class SelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget: int = Field(ge=0)
    circuits: list[Circuit] = Field(min_length=1)
    must_trim: list[str] = Field(default_factory=list)


class Selection(BaseModel):
    status: Literal["optimal", "infeasible"]
    chosen: list[str]
    cost: int
    risk_reduction: float


app = FastAPI(title="Trim selection API")


@app.post("/selections")
def select(request: SelectionRequest) -> Selection:
    # TODO: write the model (formulation first), solve it with HiGHS through MathOpt, and answer.
    # An infeasible request is still answered with 200; a must_trim id that names no circuit is not.
    return Selection(status="optimal", chosen=[], cost=0, risk_reduction=0.0)


if __name__ == "__main__":
    print(sorted(app.openapi()["paths"]))
