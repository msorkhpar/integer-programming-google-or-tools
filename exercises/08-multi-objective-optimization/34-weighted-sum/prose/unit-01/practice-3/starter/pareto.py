from __future__ import annotations


def dominates(p: tuple[float, ...], q: tuple[float, ...], senses: tuple[str, ...]) -> bool:
    """p is at least as good as q in every measure and strictly better in one."""
    # TODO
    return False


def unbeaten(options: dict[str, tuple[float, ...]], senses: tuple[str, ...]) -> set[str]:
    """The options no other option dominates. `senses[m]` is "max" or "min" for measure m."""
    # TODO: keep each option that no other option dominates.
    return set()


if __name__ == "__main__":
    print(sorted(unbeaten({"A": (3, 1), "B": (1, 3), "C": (1, 1)}, ("max", "max"))))
