from __future__ import annotations

from itertools import product


def smallest_raise(years: dict[str, list[int]], cost: dict[str, int], caps: dict[int, int]) -> tuple[int, dict[str, int]]:
    """The least total budget increase that lets every job in the conflict be done, and the years that achieve it."""
    jobs = sorted(years)
    best = None
    for choice in product(*(years[j] for j in jobs)):
        spend = {y: 0 for y in caps}
        for job, year in zip(jobs, choice):
            spend[year] += cost[job]
        extra = sum(max(0, spend[y] - caps[y]) for y in caps)
        if best is None or extra < best[0]:
            best = (extra, dict(zip(jobs, choice)))
    return best


if __name__ == "__main__":
    print(smallest_raise({"R12": [2027, 2028], "R31": [2027]}, {"R12": 700, "R31": 600}, {2027: 1000, 2028: 500}))
