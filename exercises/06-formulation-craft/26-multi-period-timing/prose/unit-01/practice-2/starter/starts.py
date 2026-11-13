from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]          # the years it may start in, earliest first


class ScheduleError(ValueError):
    """The values are not a schedule: a value is not whole, or a project starts twice."""


def read_starts(values: dict[tuple[str, int], float], projects: list[Project],
                tol: float = 1e-6) -> dict[str, int | None]:
    """Each project's start year, or None if it is not funded."""
    # TODO: read each project's start from its values, and refuse values that are not a schedule.
    return {}


def deferrals(starts: dict[str, int | None], projects: list[Project]) -> dict[str, int]:
    """Years each funded project starts after its earliest allowed year; on-time projects are left out."""
    # TODO: compare each funded project's start with its earliest allowed year.
    return {}


if __name__ == "__main__":
    demo = [Project("W1", (2027, 2028)), Project("W2", (2028,))]
    values = {("W1", 2027): 0.0, ("W1", 2028): 1.0, ("W2", 2028): 0.0}
    found = read_starts(values, demo)
    print(found, deferrals(found, demo))
