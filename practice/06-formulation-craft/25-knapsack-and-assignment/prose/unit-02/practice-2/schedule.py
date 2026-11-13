from __future__ import annotations

from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Job:
    jid: str
    earliest: int                  # first year the job may be done
    latest: int                    # last year the job may be done
    weeks: dict = field(default_factory=dict)    # crew -> weeks that crew needs for the job
    large: bool = False            # a large-diameter main: certified crews only


@dataclass(frozen=True)
class Crew:
    cid: str
    weeks: dict                    # year -> weeks the crew is free that year
    rate: int                      # $k per week
    certified: bool = False


def build(jobs: list[Job], crews: list[Crew], years: list[int]) -> tuple[mathopt.Model, dict]:
    """Every job done once, by one crew in one year: in its window, by a crew allowed to, within the crew's weeks."""
    model = mathopt.Model(name="crews-and-years")
    x: dict = {}
    # TODO: the variables, the rows and the cost.
    return model, x

if __name__ == "__main__":
    crews = [Crew("K1", {2027: 20, 2028: 20}, 9, certified=True)]
    model, x = build([Job("J1", 2027, 2028, {"K1": 8}, large=True)], crews, [2027, 2028])
    print(len(x), "variables")
