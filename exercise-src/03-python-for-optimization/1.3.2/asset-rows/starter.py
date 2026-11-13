from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AssetRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    # TODO: give each field its real type and bounds (see the statement's table).
    asset_id: str
    kind: str
    region: str
    age: str
    weibull_beta: str
    weibull_eta: str
    rul: str
    cof: str


def parse_assets(rows: list[dict[str, str]]) -> tuple[list[AssetRow], list[tuple[int, str]]]:
    """The valid rows as AssetRow objects, and (row index, field) for each row that is not valid."""
    # TODO: validate each row; a row that fails goes to the rejected list with its first bad field.
    return [], [(-1, "not checked yet")]


if __name__ == "__main__":
    row = {"asset_id": "X1", "kind": "pole", "region": "North", "age": "30", "weibull_beta": "2.5",
           "weibull_eta": "45", "rul": "12", "cof": "300"}
    print(parse_assets([row, {**row, "age": "-1"}]))
