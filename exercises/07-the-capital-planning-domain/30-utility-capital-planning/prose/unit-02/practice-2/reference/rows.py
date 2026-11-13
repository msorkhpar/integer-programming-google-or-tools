from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    program: str
    earliest: int
    latest: int
    duration: int                  # years of work
    must_do: bool = False
    alt_group: str | None = None
    parent: str | None = None
    lag: int = 0


def rows_for(pid: str, projects: list[Project], years: list[int]) -> set[str]:
    """The names of every row in which one of project `pid`'s start variables appears."""
    p = next(q for q in projects if q.pid == pid)
    starts = range(p.earliest, p.latest + 1)
    rows = {f"must_{pid}" if p.must_do else f"once_{pid}"}
    if p.alt_group:
        rows.add(f"alt_{p.alt_group}")
    if p.parent:
        rows |= {f"after_{pid}_{t}" for t in starts}
    for c in projects:
        if c.parent == pid:
            rows |= {f"after_{c.pid}_{t}" for t in range(c.earliest, c.latest + 1) if t - c.lag >= p.earliest}
    for t in starts:
        for k in range(p.duration):
            if t + k in years:
                rows |= {f"budget_{t + k}", f"crew_{p.program}_{t + k}"}
    return rows


if __name__ == "__main__":
    projects = [Project("S1", "substations", 2027, 2028, 2), Project("S2", "substations", 2029, 2029, 1, parent="S1", lag=1)]
    print(sorted(rows_for("S1", projects, [2027, 2028, 2029])))
