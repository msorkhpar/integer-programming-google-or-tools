from __future__ import annotations


def start_to_start(kind: str, lag: int, parent_duration: int, child_duration: int) -> int:
    """The same rule as a start-to-start lag L: the child may start in year t only if t >= parent start + L.

    kind names the two events the lag is measured between: "SS" (start to start), "FS" (parent's
    finish to child's start), "FF" (finish to finish) or "SF" (parent's start to child's finish).
    A project of duration d started in year s finishes at s + d.
    """
    if kind == "SS":
        return lag
    if kind == "FS":
        return parent_duration + lag
    if kind == "FF":
        return parent_duration + lag - child_duration
    if kind == "SF":
        return lag - child_duration
    raise ValueError(f"unknown lag kind {kind!r}")


def usable_child_years(parent_starts: tuple[int, ...], child_starts: tuple[int, ...], lag: int) -> list[int]:
    """The child's start years that at least one parent start serves (s <= t - lag), in order."""
    return sorted(t for t in child_starts if any(s <= t - lag for s in parent_starts))


if __name__ == "__main__":
    print(start_to_start("FS", 1, 3, 2), usable_child_years((2027,), (2027, 2028, 2030, 2031), 2))
