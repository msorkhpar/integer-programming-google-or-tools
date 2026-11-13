from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    years: tuple[int, ...]
    crew: str
    follows: str | None = None
    lag: int = 0


def conflicts(jobs: dict[str, Job], overrides: list[tuple]) -> set[str]:
    """The jobs that take part in a conflict between the overrides and the model's rules."""
    # TODO: compare the locks and bans with each other and with the jobs' rules.
    return {"?"}


if __name__ == "__main__":
    jobs = {"BRAKES": Job((2027, 2028), "north"), "WHEELS": Job((2028,), "north")}
    print(conflicts(jobs, [("lock", "BRAKES", 2028), ("lock", "WHEELS", 2028)]))
