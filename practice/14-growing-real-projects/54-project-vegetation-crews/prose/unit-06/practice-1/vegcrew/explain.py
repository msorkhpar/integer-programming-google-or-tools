"""Why a season has no plan: the planner's rules that cannot all hold together, in the planner's words.

Every rule a planner can change (a must, the budget, an override) sits behind a literal (model.py). The
search takes those literals as assumptions; when it proves the season infeasible, CP-SAT names a set of
assumptions that is enough for the proof, and a deletion filter shrinks it to a minimal one: drop each
rule in turn, and keep it out only if the rest still cannot hold.
"""

from __future__ import annotations

from ortools.sat.python import cp_model

from vegcrew.data import Override, Season
from vegcrew.model import TrimModel, build


def holds(tm: TrimModel, names: list[str]) -> bool:
    """Answers whether the named rules can all hold at once: clears the model's assumptions, adds the named rules' literals as assumptions, and solves with num_workers = 1 and stop_after_first_solution = True; True unless the status is INFEASIBLE."""
    return True


def conflict(tm: TrimModel) -> list[str]:
    """Returns a minimal list of rule names that cannot all hold, or [] when every rule can: the rules the solver names as sufficient for infeasibility (assumptions need one worker), then each dropped in turn and left out when the rest still cannot hold. The names come back in the order the rules were made, whatever order the solver named them in."""
    return []


def why_infeasible(season: Season, overrides: tuple[Override, ...] = ()) -> list[str]:
    """Builds the model of the season and its overrides and returns the words (TrimModel.says) of the rules in its conflict, in the conflict's order. The tests compare the explanation with an exact tuple in that order: musts, then the budget, then the overrides."""
    return []
