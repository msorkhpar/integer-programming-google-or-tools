from __future__ import annotations


def why_deferred(name: str, group_of: dict[str, str], best: set[str], forced: set[str] | None) -> list[str]:
    """Reasons a main left out of the best plan stays out, from the plan forced to include it.

    `group_of` maps a main to its alternative group (mains without one are absent). `forced` is the
    best plan with `name` forced in, or None when no plan allows it.
    """
    # TODO: an infeasible forcing, then what the forced plan dropped, split by alternative group.
    return []

if __name__ == "__main__":
    print(why_deferred("reline_M4", {"reline_M4": "M4", "replace_M4": "M4"}, {"replace_M4", "valve_V2"},
                       {"reline_M4"}))
