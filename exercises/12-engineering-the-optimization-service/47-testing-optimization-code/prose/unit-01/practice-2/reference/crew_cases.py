"""Hand-made cases that pin down the crew rule of a tree-trimming contractor's model."""

from __future__ import annotations

YEARS = (2027, 2028, 2029)

# One case: (jobs, crews, plan, allowed)
#   jobs:    {job: (crew-months in each year of work, first allowed start, last allowed start)}
#   crews:   {year: crew-months available}, one entry for every year of YEARS
#   plan:    {job: start year}; a job not in the plan is not started
#   allowed: True if the crew rule accepts the plan, False if it refuses it


def cases() -> list[tuple[dict, dict, dict, bool]]:
    return [
        ({"oak": ((2,), 2027, 2027)}, {2027: 2, 2028: 2, 2029: 2}, {"oak": 2027}, True),
        ({"elm": ((3,), 2029, 2029)}, {2027: 5, 2028: 5, 2029: 2}, {"elm": 2029}, False),
        ({"ash": ((2, 2), 2027, 2027)}, {2027: 3, 2028: 3, 2029: 3}, {"ash": 2027}, True),
        ({"fir": ((5,), 2027, 2027)}, {2027: 4, 2028: 4, 2029: 4}, {"fir": 2027}, False),
    ]


if __name__ == "__main__":
    for jobs, crews, plan, verdict in cases():
        print(plan, "allowed" if verdict else "refused")
