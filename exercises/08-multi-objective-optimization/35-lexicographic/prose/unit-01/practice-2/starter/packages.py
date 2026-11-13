from __future__ import annotations


def accepted(packages: dict[str, dict[str, float]],
             levels: list[tuple[str, bool, float, float]]) -> list[str]:
    """Names of the packages that survive every level, sorted."""
    # TODO: for each level, the best among the survivors, the allowed loss, then filter.
    return []


if __name__ == "__main__":
    packages = {"north": {"safety": 40, "cost": 3.0}, "south": {"safety": 39, "cost": 2.2},
                "east": {"safety": 31, "cost": 1.5}}
    print(accepted(packages, [("safety", True, 0.0, 0.05), ("cost", False, 0.0, 0.0)]))
