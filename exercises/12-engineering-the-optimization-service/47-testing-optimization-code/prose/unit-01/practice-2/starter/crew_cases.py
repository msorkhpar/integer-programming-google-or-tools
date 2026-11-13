"""Hand-made cases that pin down the crew rule of a tree-trimming contractor's model."""

from __future__ import annotations

YEARS = (2027, 2028, 2029)

# One case: (jobs, crews, plan, allowed)
#   jobs:    {job: (crew-months in each year of work, first allowed start, last allowed start)}
#   crews:   {year: crew-months available}, one entry for every year of YEARS
#   plan:    {job: start year}; a job not in the plan is not started
#   allowed: True if the crew rule accepts the plan, False if it refuses it


def cases() -> list[tuple[dict, dict, dict, bool]]:
    # TODO: hand-made instances where the crew rule alone decides, each with a plan and its verdict.
    return []

if __name__ == "__main__":
    for jobs, crews, plan, verdict in cases():
        print(plan, "allowed" if verdict else "refused")
