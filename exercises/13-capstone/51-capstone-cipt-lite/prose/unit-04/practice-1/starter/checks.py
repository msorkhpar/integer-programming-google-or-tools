from __future__ import annotations

Finding = tuple[str, str]                         # (rule, subject)


def starts(project: dict) -> list[int]:
    return list(range(project["earliest"], project["latest"] + 1))


def spend(project: dict, start: int) -> dict[int, int]:
    """What the project spends in each calendar year if it starts in `start`."""
    return {start + k: amount for k, amount in enumerate(project["cost"])}


def budgets(snapshot: dict, scenario: dict) -> dict[int, int]:
    return {y: scenario.get("budget", {}).get(y, snapshot["budget"][y]) for y in snapshot["years"]}


def crews(snapshot: dict, scenario: dict, program: str, year: int) -> int:
    return scenario.get("crews", {}).get(program, {}).get(year, snapshot["crews"][program][year])


def required(snapshot: dict, scenario: dict) -> dict[str, list[int]]:
    """Every project each plan must fund, with the start years left to it."""
    # TODO: must-dos and forced projects get their windows; a fixed start leaves one year.
    return {}


def checks(snapshot: dict, scenario: dict) -> list[Finding]:
    """Every finding of the six rules, in the order the statement gives."""
    # TODO
    return [("not checked", "")]


if __name__ == "__main__":
    snapshot = {"years": [2027], "budget": {2027: 100}, "crews": {"lines": {2027: 2}}, "floor": {},
                "projects": {"J1": {"program": "lines", "region": "North", "cost": [150], "earliest": 2027,
                                    "latest": 2027, "must": True, "group": None, "crews": 1}}}
    print(checks(snapshot, {"name": "lock"}))
