from __future__ import annotations

from pydantic import BaseModel, model_validator


class Bus(BaseModel):
    # TODO: a bound on cost.
    bus_id: str
    depot: str
    cost: int                                   # $k
    earliest: int
    latest: int

    @model_validator(mode="after")
    def window_holds_a_year(self):
        # TODO: refuse a window that holds no year.
        return self


class YearBudget(BaseModel):
    # TODO: a budget cannot be negative.
    year: int
    amount: int                                 # $k


class FleetSnapshot(BaseModel):
    schema_version: int
    horizon: list[int]
    depots: list[str]
    budgets: list[YearBudget]
    buses: list[Bus]

    @model_validator(mode="after")
    def references_resolve(self):
        problems: list[str] = []
        # TODO: every rule across records; add one message per problem found.
        if problems:
            raise ValueError("; ".join(problems))
        return self


if __name__ == "__main__":
    text = ('{"schema_version": 3, "horizon": [2027], "depots": ["North"], '
            '"budgets": [{"year": 2027, "amount": 900}], '
            '"buses": [{"bus_id": "B101", "depot": "North", "cost": 450, "earliest": 2027, "latest": 2027}]}')
    print(FleetSnapshot.model_validate_json(text))
