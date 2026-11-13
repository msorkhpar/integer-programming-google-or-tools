"""Properties every plan of a water utility's main-replacement selection must obey.

An instance is a dict:
    "cost":   {project: (capital $k, operating $k)}
    "budget": (capital budget $k, operating budget $k)
    "must":   [projects that must be funded]
    "needs":  {project: [its prerequisites]}, every project a key
    "value":  {project: value}
A plan is the set of funded projects. Each property returns None when it holds and fails an
`assert` when it does not, so Hypothesis can use it as the body of a test.
"""

from __future__ import annotations


def within_both_budgets(instance: dict, plan: set[str]) -> None:
    """The plan's capital and its operating spend each fit their budget."""
    # TODO


def must_dos_funded(instance: dict, plan: set[str]) -> None:
    """Every must-do project is funded."""
    # TODO


def prerequisites_funded(instance: dict, plan: set[str]) -> None:
    """No funded project lacks a prerequisite."""
    # TODO


if __name__ == "__main__":
    example = {"cost": {"w1": (30, 2), "w2": (20, 1)}, "budget": (40, 5), "must": ["w1"],
               "needs": {"w1": [], "w2": ["w1"]}, "value": {"w1": 5, "w2": 4}}
    for check in (within_both_budgets, must_dos_funded, prerequisites_funded):
        check(example, {"w1"})
    print("{'w1'} keeps all three properties")
