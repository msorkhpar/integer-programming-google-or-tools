from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError


class Contract(BaseModel):
    # TODO: the policy for a document sent by another program.
    pass


class Bus(Contract):
    bus_id: str
    depot: str
    cost: int                                   # $k
    must_replace: bool


class Fleet(Contract):
    schema_version: int                         # TODO: only version 3 is valid here
    buses: tuple[Bus, ...]


def upgrade(raw: dict) -> dict:
    """Version 2 called the depot `garage` and had no `must_replace`: nothing was mandatory then."""
    # TODO: bring a version-2 document up to version 3; leave every other document alone.
    return raw


def parse(text: str) -> Fleet | None:
    """The fleet if the document is valid in version 3 (after upgrading version 2), else None."""
    try:
        return Fleet.model_validate_json(json.dumps(upgrade(json.loads(text))))
    except ValidationError:
        return None


if __name__ == "__main__":
    print(parse('{"schema_version": 2, "buses": [{"bus_id": "B7", "garage": "North", "cost": 400}]}'))
