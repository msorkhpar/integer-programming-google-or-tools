from __future__ import annotations


def why_deferred(name: str, group_of: dict[str, str], best: set[str], forced: set[str] | None) -> list[str]:
    """Reasons a main left out of the best plan stays out, from the plan forced to include it.

    `group_of` maps a main to its alternative group (mains without one are absent). `forced` is the
    best plan with `name` forced in, or None when no plan allows it.
    """
    if forced is None:
        return ["infeasible"]
    dropped = sorted(best - forced - {name})
    if not dropped:
        return ["nothing displaced"]
    group = group_of.get(name)
    alternatives = [f"alternative {m}" for m in dropped if group is not None and group_of.get(m) == group]
    displaced = [f"displaced {m}" for m in dropped if group is None or group_of.get(m) != group]
    return alternatives + displaced


if __name__ == "__main__":
    print(why_deferred("reline_M4", {"reline_M4": "M4", "replace_M4": "M4"}, {"replace_M4", "valve_V2"},
                       {"reline_M4"}))
