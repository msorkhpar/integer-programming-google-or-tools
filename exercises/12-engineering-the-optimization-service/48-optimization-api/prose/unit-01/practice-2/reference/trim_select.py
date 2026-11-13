from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from ortools.math_opt.python import mathopt
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
    known = {c.circuit_id for c in request.circuits}
    if len(known) < len(request.circuits):
        raise HTTPException(status_code=422, detail="circuit ids must be unique")
    unknown = sorted(set(request.must_trim) - known)
    if unknown:
        raise HTTPException(status_code=422, detail=f"must_trim names unknown circuits {unknown}")
    model = mathopt.Model(name="trim selection")
    y = {c.circuit_id: model.add_binary_variable(name=f"y_{c.circuit_id}") for c in request.circuits}
    model.add_linear_constraint(sum(c.cost * y[c.circuit_id] for c in request.circuits) <= request.budget,
                                name="budget")
    for cid in request.must_trim:
        model.add_linear_constraint(y[cid] == 1, name=f"must_{cid}")
    model.maximize(sum(c.risk_reduction * y[c.circuit_id] for c in request.circuits))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason == mathopt.TerminationReason.INFEASIBLE:
        return Selection(status="infeasible", chosen=[], cost=0, risk_reduction=0.0)
    values = result.variable_values()
    chosen = sorted(cid for cid, var in y.items() if values[var] > 0.5)
    by_id = {c.circuit_id: c for c in request.circuits}
    return Selection(status="optimal", chosen=chosen, cost=sum(by_id[c].cost for c in chosen),
                     risk_reduction=sum(by_id[c].risk_reduction for c in chosen))


if __name__ == "__main__":
    print(sorted(app.openapi()["paths"]))
