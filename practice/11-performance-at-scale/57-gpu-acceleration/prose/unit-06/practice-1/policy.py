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
    # TODO: the rules of the statement, one branch each; every branch without a GPU is a CPU branch.
    return Policy("", "", "", 0, 0.0, False)


if __name__ == "__main__":
    print(decide({"kind": "lp", "nonzeros": 2_000_000, "use": "explore"}, {"gpu": True, "cuopt": True, "cores": 16}))
