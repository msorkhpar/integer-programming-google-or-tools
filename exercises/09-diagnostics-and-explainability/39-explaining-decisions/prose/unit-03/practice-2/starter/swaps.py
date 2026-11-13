from __future__ import annotations


def pair_swaps(adds: list[str], drops: list[str], group_of: dict[str, str]) -> dict:
    """Pair each dropped option with the option of the same alternative group that was added."""
    # TODO: find the swaps, then what is left of each list.
    return {"swaps": [], "adds": [], "drops": []}

if __name__ == "__main__":
    print(pair_swaps(["reline_M4"], ["replace_M4"], {"reline_M4": "M4", "replace_M4": "M4"}))
