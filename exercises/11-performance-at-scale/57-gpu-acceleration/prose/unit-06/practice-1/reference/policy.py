from __future__ import annotations

from dataclasses import dataclass

LARGE = 500_000          # nonzeros from which an LP goes to the GPU


@dataclass(frozen=True)
class Policy:
    device: str
    solver: str
    method: str
    threads: int
    tolerance: float
    verify: bool


def decide(job: dict, machine: dict) -> Policy:
    """The run policy for one job on one machine."""
    if job["use"] == "publish":
        if job["kind"] == "milp":
            return Policy("cpu", "highs", "branch-and-bound", 1, 1e-4, False)
        return Policy("cpu", "highs", "simplex", 1, 1e-7, False)
    if job["kind"] == "milp":
        if machine["gpu"] and machine["cuopt"]:
            return Policy("gpu", "cuopt", "milp", machine["cores"], 1e-2, True)
        return Policy("cpu", "highs", "branch-and-bound", min(4, machine["cores"]), 1e-2, False)
    if job["nonzeros"] >= LARGE:
        if machine["gpu"]:
            return Policy("gpu", "highs", "pdlp", 1, 1e-6, True)
        return Policy("cpu", "highs", "ipm", min(4, machine["cores"]), 1e-8, False)
    return Policy("cpu", "highs", "simplex", 1, 1e-7, False)


if __name__ == "__main__":
    print(decide({"kind": "lp", "nonzeros": 2_000_000, "use": "explore"}, {"gpu": True, "cuopt": True, "cores": 16}))
