from __future__ import annotations

from typing import Callable


def conflict_among(soft: list[str], hard: list[str], infeasible: Callable[[set[str]], bool]) -> list[str] | None:
    """The soft rules of one irreducible conflict, with every hard rule always on.

    None if all the rules together are feasible; [] if the hard rules alone are infeasible.
    """
    # TODO: a deletion filter over the soft rules only; the hard rules are in every question.
    return None


if __name__ == "__main__":
    clash = [{"room_cap_B12", "class_7A_in_B12"}]
    print(conflict_among(["class_7A_in_B12", "teacher_off_fri"], ["room_cap_B12"],
                         lambda on: any(c <= on for c in clash)))
