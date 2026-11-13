from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Circuit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    circuit_id: str = Field(min_length=1)
    miles: float = Field(gt=0)
    cost: int = Field(ge=0)


class TrimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget: int = Field(ge=0)
    circuits: list[Circuit] = Field(min_length=1)

    @model_validator(mode="after")
    def ids_are_unique(self) -> "TrimRequest":
        ids = [c.circuit_id for c in self.circuits]
        if len(ids) != len(set(ids)):
            raise ValueError("circuit ids must be unique")
        return self


app = FastAPI(title="Trim planning API")


@app.post("/trims")
def accept(request: TrimRequest) -> dict:
    return {"circuits": len(request.circuits), "budget": request.budget}


if __name__ == "__main__":
    print(TrimRequest.model_json_schema()["required"])
