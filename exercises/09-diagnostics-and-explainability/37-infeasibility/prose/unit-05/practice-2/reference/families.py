from __future__ import annotations

from typing import Callable


def two_pass(families: dict[str, list[str]], infeasible: Callable[[set[str]], bool]) -> tuple[list[str], list[str]]:
    """A deletion filter over whole families, then over the rules of the families it kept."""
    kept = list(families)
    for family in families:
        trial = [f for f in kept if f != family]
        if infeasible({r for f in trial for r in families[f]}):
            kept = trial
    rules = [r for f in kept for r in families[f]]
    conflict = list(rules)
    for rule in rules:
        trial = [r for r in conflict if r != rule]
        if infeasible(set(trial)):
            conflict = trial
    return kept, conflict


if __name__ == "__main__":
    families = {"budget": ["budget_2027", "budget_2028"], "crews": ["crews_east"], "must": ["must_A"]}
    clash = [{"budget_2028", "must_A"}]
    print(two_pass(families, lambda on: any(c <= on for c in clash)))
