from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AssetRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    asset_id: str
    kind: str
    region: Literal["North", "South", "East", "West"]
    age: int = Field(ge=0)
    weibull_beta: float = Field(gt=0)
    weibull_eta: float = Field(gt=0)
    rul: int = Field(ge=0)
    cof: int = Field(ge=0)


def parse_assets(rows: list[dict[str, str]]) -> tuple[list[AssetRow], list[tuple[int, str]]]:
    """The valid rows as AssetRow objects, and (row index, field) for each row that is not valid."""
    assets, rejected = [], []
    for index, row in enumerate(rows):
        try:
            assets.append(AssetRow.model_validate(row))
        except ValidationError as error:
            rejected.append((index, str(error.errors()[0]["loc"][0])))
    return assets, rejected


if __name__ == "__main__":
    row = {"asset_id": "X1", "kind": "pole", "region": "North", "age": "30", "weibull_beta": "2.5",
           "weibull_eta": "45", "rul": "12", "cof": "300"}
    print(parse_assets([row, {**row, "age": "-1"}]))
