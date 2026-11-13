from __future__ import annotations


def start_to_start(kind: str, lag: int, parent_duration: int, child_duration: int) -> int:
    """The same rule as a start-to-start lag L: the child may start in year t only if t >= parent start + L.

    kind names the two events the lag is measured between: "SS" (start to start), "FS" (parent's
    finish to child's start), "FF" (finish to finish) or "SF" (parent's start to child's finish).
    A project of duration d started in year s finishes at s + d.
    """
    # TODO: convert each kind of lag to start-to-start.
    return lag


def usable_child_years(parent_starts: tuple[int, ...], child_starts: tuple[int, ...], lag: int) -> list[int]:
    """The child's start years that at least one parent start serves (s <= t - lag), in order."""
    # TODO: keep only the child years some parent start can serve.
    return list(child_starts)


if __name__ == "__main__":
    print(start_to_start("FS", 1, 3, 2), usable_child_years((2027,), (2027, 2028, 2030, 2031), 2))
