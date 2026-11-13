from __future__ import annotations


def accepted(packages: dict[str, dict[str, float]],
             levels: list[tuple[str, bool, float, float]]) -> list[str]:
    """Names of the packages that survive every level, sorted."""
    alive = dict(packages)
    for name, maximize, abs_tol, rel_tol in levels:
        values = [v[name] for v in alive.values()]
        best = max(values) if maximize else min(values)
        loss = max(abs_tol, rel_tol * abs(best))
        if maximize:
            alive = {k: v for k, v in alive.items() if v[name] >= best - loss}
        else:
            alive = {k: v for k, v in alive.items() if v[name] <= best + loss}
    return sorted(alive)


if __name__ == "__main__":
    packages = {"north": {"safety": 40, "cost": 3.0}, "south": {"safety": 39, "cost": 2.2},
                "east": {"safety": 31, "cost": 1.5}}
    print(accepted(packages, [("safety", True, 0.0, 0.05), ("cost", False, 0.0, 0.0)]))
