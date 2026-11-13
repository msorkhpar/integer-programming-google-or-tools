from __future__ import annotations


def name_crews(jobs: dict[str, tuple[int, int, int]], crews: list[str]) -> dict[str, list[str]]:
    """Crew names for each job of a pool schedule, handed out in order of start day."""
    free_from = {c: 0 for c in crews}
    named = {}
    for name, (start, days, need) in sorted(jobs.items(), key=lambda item: (item[1][0], item[0])):
        free = sorted(c for c, f in free_from.items() if f <= start)
        named[name] = free[:need]
        for c in named[name]:
            free_from[c] = start + days
    return named


if __name__ == "__main__":
    print(name_crews({"hedge": (0, 3, 2), "lawn": (0, 2, 1), "pond": (2, 4, 1), "path": (3, 2, 2)}, ["A", "B", "C"]))
