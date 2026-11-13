from __future__ import annotations


def name_crews(jobs: dict[str, tuple[int, int, int]], crews: list[str]) -> dict[str, list[str]]:
    """Crew names for each job of a pool schedule, handed out in order of start day."""
    # TODO: go through the jobs by start day, give each the crews free on that day, and mark them
    # busy until the job ends. Every list below is a placeholder.
    return {name: [] for name in jobs}


if __name__ == "__main__":
    print(name_crews({"hedge": (0, 3, 2), "lawn": (0, 2, 1), "pond": (2, 4, 1), "path": (3, 2, 2)}, ["A", "B", "C"]))
