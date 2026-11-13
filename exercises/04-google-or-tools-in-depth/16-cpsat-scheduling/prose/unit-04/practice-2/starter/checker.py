from __future__ import annotations


def broken_rules(jobs: dict[str, tuple[int, int, list[tuple[int, int]] | None]], start: dict[str, int],
                 installers: int, horizon: int) -> set[tuple[str, object]]:
    """Every rule the plan breaks: ("outside", job), ("window", job), ("crowded", day)."""
    # TODO: one loop per rule. The placeholder below reports a rule nobody wrote.
    return {("unchecked", "plan")}


if __name__ == "__main__":
    jobs = {"drill": (2, 2, [(0, 3)]), "paint": (3, 1, None), "hang": (1, 3, None)}
    print(broken_rules(jobs, {"drill": 2, "paint": 0, "hang": 4}, 3, 6))
