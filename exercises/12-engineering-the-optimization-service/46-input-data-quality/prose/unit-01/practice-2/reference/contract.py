from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Bus(Contract):
    bus_id: str
    depot: str
    cost: int                                   # $k
    must_replace: bool


class Fleet(Contract):
    schema_version: Literal[3]
    buses: tuple[Bus, ...]


def upgrade(raw: dict) -> dict:
    """Version 2 called the depot `garage` and had no `must_replace`: nothing was mandatory then."""
    if raw.get("schema_version") == 2:
        if any("depot" in b or "must_replace" in b for b in raw["buses"]):
            return raw                          # keys version 2 never had: left for the schema to refuse
        buses = [{**{("depot" if k == "garage" else k): v for k, v in b.items()}, "must_replace": False}
                 for b in raw["buses"]]
        raw = {**raw, "buses": buses, "schema_version": 3}
    return raw


def parse(text: str) -> Fleet | None:
    """The fleet if the document is valid in version 3 (after upgrading version 2), else None."""
    try:
        return Fleet.model_validate_json(json.dumps(upgrade(json.loads(text))))
    except ValidationError:
        return None


if __name__ == "__main__":
    print(parse('{"schema_version": 2, "buses": [{"bus_id": "B7", "garage": "North", "cost": 400}]}'))
