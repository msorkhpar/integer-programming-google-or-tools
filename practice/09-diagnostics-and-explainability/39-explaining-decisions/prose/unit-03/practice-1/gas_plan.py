from __future__ import annotations


def quarters(start: str) -> int:
    """'2028-Q3' as a count of quarters, so that later starts are larger and a year has four."""
    # TODO
    return 0


def diff_scenarios(a: dict, b: dict) -> dict:
    """What changed from scenario a's plan to scenario b's: adds, drops and timing shifts in quarters."""
    # TODO: match the two plans by project id.
    return {"adds": [], "drops": [], "shifts": []}

if __name__ == "__main__":
    spring = {"name": "spring", "plan": [{"id": "PR-11", "start": "2028-Q1"}]}
    summer = {"name": "summer", "plan": [{"id": "PR-11", "start": "2028-Q3"}]}
    print(diff_scenarios(spring, summer))
