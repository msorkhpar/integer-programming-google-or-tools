from __future__ import annotations

from typing import Callable


def audit(claim: list[str], infeasible: Callable[[set[str]], bool]) -> dict:
    """Check a claimed conflict: is it infeasible, and which members could be dropped and leave it so?"""
    if not infeasible(set(claim)):
        return {"infeasible": False, "not_needed": []}
    not_needed = [r for r in claim if infeasible(set(claim) - {r})]
    return {"infeasible": True, "not_needed": not_needed}


if __name__ == "__main__":
    clash = [{"track_closed_wk12", "grind_wk12"}]
    print(audit(["track_closed_wk12", "grind_wk12", "crew_max_3"], lambda on: any(c <= on for c in clash)))
