from __future__ import annotations


def pair_swaps(adds: list[str], drops: list[str], group_of: dict[str, str]) -> dict:
    """Pair each dropped option with the option of the same alternative group that was added."""
    added_by_group = {group_of[p]: p for p in adds if p in group_of}
    swaps, paired = [], set()
    for old in sorted(drops):
        group = group_of.get(old)
        new = added_by_group.get(group) if group is not None else None
        if new is not None:
            swaps.append((old, new))
            paired |= {old, new}
    return {"swaps": swaps,
            "adds": sorted(p for p in adds if p not in paired),
            "drops": sorted(p for p in drops if p not in paired)}


if __name__ == "__main__":
    print(pair_swaps(["reline_M4"], ["replace_M4"], {"reline_M4": "M4", "replace_M4": "M4"}))
