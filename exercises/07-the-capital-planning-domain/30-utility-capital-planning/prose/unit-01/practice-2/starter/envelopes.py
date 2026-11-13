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
    # TODO: spread each request's profile over the years it is worked. The zeros are placeholders.
    return {g: {y: 0 for y in years} for g in programs}


def oversubscribed(requests: list[Request], envelopes: dict[tuple[str, int], int]) -> list[tuple[str, int, int, int]]:
    """(program, year, requested, excess) for every envelope the requests exceed, sorted."""
    # TODO: compare each envelope with what is requested in its program and year.
    return []


if __name__ == "__main__":
    reqs = [Request("M1", "mains", 2027, (300, 200)), Request("T1", "treatment", 2028, (900,))]
    print(requested_by_year(reqs, ["mains", "treatment"], [2027, 2028]))
    print(oversubscribed(reqs, {("mains", 2027): 250, ("treatment", 2028): 1_000}))
