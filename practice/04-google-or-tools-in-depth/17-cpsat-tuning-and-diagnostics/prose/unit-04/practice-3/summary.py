from __future__ import annotations


def read_summary(log: str) -> dict[str, str]:
    """The `key: value` lines of the CpSolverResponse summary block, as strings."""
    # TODO: the lines after "CpSolverResponse summary:".
    return {}


def relative_gap(log: str) -> float:
    """|objective - best_bound| / max(1, |objective|), the gap the parameters proto defines."""
    return -1.0


if __name__ == "__main__":
    print(relative_gap("CpSolverResponse summary:\nstatus: FEASIBLE\nobjective: 200\nbest_bound: 210\n"))
