"""A pydantic model of one projects.csv row: it converts each field to its type or says why it cannot."""

import csv
import json
from typing import Literal

from pydantic import (BaseModel, ConfigDict, Field, NonNegativeInt, TypeAdapter, ValidationError,
                      field_validator, model_validator)

from export import dirty_export

Program = Literal["transmission", "distribution", "vegetation"]
Region = Literal["Ridge", "Valley", "Coast", "Plains"]


class ProjectRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    project_id: str
    program: Program
    region: Region
    cost_profile: tuple[NonNegativeInt, ...]
    earliest_start: int
    latest_start: int
    must_do: bool
    parent: str | None
    alt_group: str | None

    @field_validator("cost_profile", mode="before")
    @classmethod
    def split_years(cls, value):
        return value.split(";") if isinstance(value, str) else value

    @field_validator("parent", "alt_group", mode="before")
    @classmethod
    def blank_is_none(cls, value):
        return value or None

    @model_validator(mode="after")
    def window_is_ordered(self):
        if self.earliest_start > self.latest_start:
            raise ValueError("earliest start after latest")
        return self


class PlanSettings(BaseModel):
    """The two numbers of portfolio.json the models use."""
    discount_rate: float = Field(gt=0)
    capital_budget: NonNegativeInt


def reasons(error: ValidationError) -> list[str]:
    """Each problem pydantic found, as `field: message` (a whole-row rule has no field)."""
    return [f"{'.'.join(str(part) for part in e['loc']) or 'row'}: {e['msg']}" for e in error.errors()]


def convert(kind: type, texts: tuple[str, ...]) -> None:
    """Show what pydantic's default (lax) mode makes of each text for a field of type `kind`."""
    adapter = TypeAdapter(kind)
    for text in texts:
        try:
            print(f"{kind.__name__:4} {text!r:9} -> {adapter.validate_python(text)!r}")
        except ValidationError as error:
            print(f"{kind.__name__:4} {text!r:9} -> rejected: {error.errors()[0]['msg']}")


if __name__ == "__main__":
    convert(int, ("2150", " 2150 ", "2150.0", "2150.5", "2,150"))
    convert(bool, ("0", "1", "yes", "2"))
    try:
        TypeAdapter(int, config=ConfigDict(strict=True)).validate_python("2150")
    except ValidationError as error:
        print("strict int '2150' -> rejected:", error.errors()[0]["msg"])
    print()

    with dirty_export() as folder:
        with (folder / "projects.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        settings = json.loads((folder / "portfolio.json").read_text(encoding="utf-8"))

    p003 = ProjectRow.model_validate(rows[2])
    print(p003)
    print("P003 lasts", len(p003.cost_profile), "years and costs", sum(p003.cost_profile))
    print("P001 is must-do:", ProjectRow.model_validate(rows[0]).must_do)

    print()
    print(PlanSettings.model_validate(settings))
    for rate in ("0", "", "0.07"):
        try:
            print(f"discount_rate {rate!r:6} ->", PlanSettings.model_validate({**settings, "discount_rate": rate}))
        except ValidationError as error:
            print(f"discount_rate {rate!r:6} -> rejected:", error.errors()[0]["msg"])

    print()
    for row in (rows[9], {**settings, "discount_rate": "0"}):
        model = ProjectRow if "project_id" in row else PlanSettings
        try:
            model.model_validate(row)
        except ValidationError as error:
            entry = error.errors()[0]                # one dict per problem
            print({key: entry[key] for key in ("type", "loc", "msg", "input")})

    print()
    for row in rows[8:]:
        try:
            ProjectRow.model_validate(row)
            print(row["project_id"], "accepted")
        except ValidationError as error:
            print(row["project_id"], "rejected:", "; ".join(reasons(error)))
