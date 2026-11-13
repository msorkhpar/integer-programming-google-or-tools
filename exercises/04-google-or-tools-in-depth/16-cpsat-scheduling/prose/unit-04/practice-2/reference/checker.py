from __future__ import annotations


def broken_rules(jobs: dict[str, tuple[int, int, list[tuple[int, int]] | None]], start: dict[str, int],
                 installers: int, horizon: int) -> set[tuple[str, object]]:
    """Every rule the plan breaks: ("outside", job), ("window", job), ("crowded", day)."""
    broken = set()
    for name, (days, _, windows) in jobs.items():
        s, e = start[name], start[name] + days
        if s < 0 or e > horizon:
            broken.add(("outside", name))
        if windows is not None and not any(a <= s and e <= b for a, b in windows):
            broken.add(("window", name))
    for t in range(horizon):
        used = sum(need for name, (days, need, _) in jobs.items() if start[name] <= t < start[name] + days)
        if used > installers:
            broken.add(("crowded", t))
    return broken


if __name__ == "__main__":
    jobs = {"drill": (2, 2, [(0, 3)]), "paint": (3, 1, None), "hang": (1, 3, None)}
    print(broken_rules(jobs, {"drill": 2, "paint": 0, "hang": 4}, 3, 6))
