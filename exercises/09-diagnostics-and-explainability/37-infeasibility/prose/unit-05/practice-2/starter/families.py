from __future__ import annotations

from typing import Callable


def two_pass(families: dict[str, list[str]], infeasible: Callable[[set[str]], bool]) -> tuple[list[str], list[str]]:
    """A deletion filter over whole families, then over the rules of the families it kept."""
    # TODO: first pass over families, second pass over the rules of the kept families.
    return list(families), []


if __name__ == "__main__":
    families = {"budget": ["budget_2027", "budget_2028"], "crews": ["crews_east"], "must": ["must_A"]}
    clash = [{"budget_2028", "must_A"}]
    print(two_pass(families, lambda on: any(c <= on for c in clash)))
