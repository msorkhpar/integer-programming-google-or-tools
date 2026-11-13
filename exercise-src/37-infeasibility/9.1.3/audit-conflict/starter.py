from __future__ import annotations

from typing import Callable


def audit(claim: list[str], infeasible: Callable[[set[str]], bool]) -> dict:
    """Check a claimed conflict: is it infeasible, and which members could be dropped and leave it so?"""
    # TODO: first, is the claim infeasible at all? Then test each member against the rest of the claim.
    return {"infeasible": True, "not_needed": []}


if __name__ == "__main__":
    clash = [{"track_closed_wk12", "grind_wk12"}]
    print(audit(["track_closed_wk12", "grind_wk12", "crew_max_3"], lambda on: any(c <= on for c in clash)))
