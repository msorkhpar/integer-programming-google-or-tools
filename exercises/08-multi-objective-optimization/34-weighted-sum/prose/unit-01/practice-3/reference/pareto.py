from __future__ import annotations


def dominates(p: tuple[float, ...], q: tuple[float, ...], senses: tuple[str, ...]) -> bool:
    """p is at least as good as q in every measure and strictly better in one."""
    better = False
    for a, b, sense in zip(p, q, senses):
        if sense == "min":
            a, b = -a, -b
        if a < b:
            return False
        if a > b:
            better = True
    return better


def unbeaten(options: dict[str, tuple[float, ...]], senses: tuple[str, ...]) -> set[str]:
    """The options no other option dominates. `senses[m]` is "max" or "min" for measure m."""
    return {name for name, q in options.items()
            if not any(dominates(p, q, senses) for other, p in options.items() if other != name)}


if __name__ == "__main__":
    print(sorted(unbeaten({"A": (3, 1), "B": (1, 3), "C": (1, 1)}, ("max", "max"))))
