from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class Bus(BaseModel):
    bus_id: str
    depot: str
    cost: int = Field(gt=0)                     # $k
    earliest: int
    latest: int

    @model_validator(mode="after")
    def window_holds_a_year(self):
        if self.earliest > self.latest:
            raise ValueError(f"{self.bus_id}: no year between {self.earliest} and {self.latest}")
        return self


class YearBudget(BaseModel):
    year: int
    amount: int = Field(ge=0)                   # $k


class FleetSnapshot(BaseModel):
    schema_version: int
    horizon: list[int]
    depots: list[str]
    budgets: list[YearBudget]
    buses: list[Bus]

    @model_validator(mode="after")
    def references_resolve(self):
        problems: list[str] = []
        seen = set()
        for bus in self.buses:
            if bus.bus_id in seen:
                problems.append(f"bus {bus.bus_id} is listed twice")
            seen.add(bus.bus_id)
            if bus.depot not in self.depots:
                problems.append(f"bus {bus.bus_id} is at unlisted depot {bus.depot}")
        for year in self.horizon:
            rows = [b for b in self.budgets if b.year == year]
            if len(rows) != 1:
                problems.append(f"year {year} has {len(rows)} budget rows")
        if problems:
            raise ValueError("; ".join(problems))
        return self

if __name__ == "__main__":
    text = ('{"schema_version": 3, "horizon": [2027], "depots": ["North"], '
            '"budgets": [{"year": 2027, "amount": 900}], '
            '"buses": [{"bus_id": "B101", "depot": "North", "cost": 450, "earliest": 2027, "latest": 2027}]}')
    print(FleetSnapshot.model_validate_json(text))
