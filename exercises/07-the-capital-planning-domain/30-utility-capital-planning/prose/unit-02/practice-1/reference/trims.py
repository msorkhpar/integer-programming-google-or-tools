from __future__ import annotations


def plan_trims(circuits: dict[str, tuple[int, int]], cycle: int, capacity: int,
               years: list[int]) -> dict[int, tuple[list[str], int]]:
    """Year -> (circuits trimmed that year, sorted; miles due but left untrimmed at year end)."""
    last = {c: trimmed for c, (_, trimmed) in circuits.items()}
    plan = {}
    for y in years:
        due = [c for c in circuits if y - last[c] >= cycle]
        due.sort(key=lambda c: (last[c], c))           # longest since its last trim first
        left = capacity
        done = []
        for c in due:
            miles = circuits[c][0]
            if miles <= left:
                done.append(c)
                left -= miles
                last[c] = y
        plan[y] = (sorted(done), sum(circuits[c][0] for c in due if c not in done))
    return plan


if __name__ == "__main__":
    print(plan_trims({"A": (50, 2018), "B": (10, 2019), "C": (10, 2020)}, 3, 25, [2024, 2025]))
