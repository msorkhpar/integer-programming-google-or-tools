from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    rid: str
    program: str
    start: int
    profile: tuple[int, ...]          # $k spent in each year of work, from `start` on


def requested_by_year(requests: list[Request], programs: list[str], years: list[int]) -> dict[str, dict[int, int]]:
    """Program -> year -> $k the requests would spend there, with a 0 for every empty cell."""
    table = {g: {y: 0 for y in years} for g in programs}
    for r in requests:
        if r.program not in table:
            continue
        for k, amount in enumerate(r.profile):
            if r.start + k in table[r.program]:
                table[r.program][r.start + k] += amount
    return table


def oversubscribed(requests: list[Request], envelopes: dict[tuple[str, int], int]) -> list[tuple[str, int, int, int]]:
    """(program, year, requested, excess) for every envelope the requests exceed, sorted."""
    programs = sorted({g for g, _ in envelopes})
    years = sorted({y for _, y in envelopes})
    table = requested_by_year(requests, programs, years)
    over = []
    for (g, y), cap in sorted(envelopes.items()):
        if table[g][y] > cap:
            over.append((g, y, table[g][y], table[g][y] - cap))
    return over


if __name__ == "__main__":
    reqs = [Request("M1", "mains", 2027, (300, 200)), Request("T1", "treatment", 2028, (900,))]
    print(requested_by_year(reqs, ["mains", "treatment"], [2027, 2028]))
    print(oversubscribed(reqs, {("mains", 2027): 250, ("treatment", 2028): 1_000}))
