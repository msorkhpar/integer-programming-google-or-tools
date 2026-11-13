"""Summarize a back-test of a school district's roof-replacement model against past cycles.

archive: [{"cycle": year, "approved": {roof: start year}}, ...], the plans past cycles approved
rerun:   {year: {roof: start year}}, what today's model chose on each past cycle's snapshot
"""

from __future__ import annotations


def summarize(archive: list[dict], rerun: dict[int, dict[str, int]]) -> list[dict]:
    """One summary per archived cycle, in archive order."""
    # TODO: compare each archived plan with today's rerun of its cycle.
    return []

if __name__ == "__main__":
    print(summarize([{"cycle": 2024, "approved": {"gym": 2025}}], {2024: {"gym": 2026}}))
