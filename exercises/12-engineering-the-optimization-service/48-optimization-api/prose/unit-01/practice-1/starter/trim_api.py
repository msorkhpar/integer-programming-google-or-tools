from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Circuit(BaseModel):
    # TODO: refuse an empty id, miles that are not positive, a negative cost, and unknown fields.
    circuit_id: str
    miles: float
    cost: int


class TrimRequest(BaseModel):
    # TODO: refuse a negative budget, an empty circuit list, repeated circuit ids, and unknown fields.
    budget: int
    circuits: list[Circuit]


app = FastAPI(title="Trim planning API")


@app.post("/trims")
def accept(request: TrimRequest) -> dict:
    return {"circuits": len(request.circuits), "budget": request.budget}


if __name__ == "__main__":
    print(TrimRequest.model_json_schema()["required"])
