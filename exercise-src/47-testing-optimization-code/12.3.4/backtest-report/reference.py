"""Summarize a back-test of a school district's roof-replacement model against past cycles.

archive: [{"cycle": year, "approved": {roof: start year}}, ...], the plans past cycles approved
rerun:   {year: {roof: start year}}, what today's model chose on each past cycle's snapshot
"""

from __future__ import annotations


def summarize(archive: list[dict], rerun: dict[int, dict[str, int]]) -> list[dict]:
    """One summary per archived cycle, in archive order."""
    rows = []
    for entry in archive:
        cycle, was = entry["cycle"], entry["approved"]
        if cycle not in rerun:
            rows.append({"cycle": cycle, "missing": True})
            continue
        now = rerun[cycle]
        kept = sum(1 for p in was if now.get(p) == was[p])
        moved = sum(1 for p in was if p in now and now[p] != was[p])
        if was:
            agreement = round(kept / len(was), 3)
        else:
            agreement = 1.0 if not now else 0.0
        rows.append({"cycle": cycle, "missing": False, "kept": kept, "moved": moved,
                     "added": sum(1 for p in now if p not in was),
                     "dropped": sum(1 for p in was if p not in now), "agreement": agreement})
    return rows


if __name__ == "__main__":
    print(summarize([{"cycle": 2024, "approved": {"gym": 2025}}], {2024: {"gym": 2026}}))
