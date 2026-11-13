from __future__ import annotations


def read_summary(log: str) -> dict[str, str]:
    """The `key: value` lines of the CpSolverResponse summary block, as strings."""
    lines = log.splitlines()
    start = lines.index("CpSolverResponse summary:") + 1
    out = {}
    for line in lines[start:]:
        if ": " not in line:
            break
        key, value = line.split(": ", 1)
        out[key] = value
    return out


def relative_gap(log: str) -> float:
    """|objective - best_bound| / max(1, |objective|), the gap the parameters proto defines."""
    summary = read_summary(log)
    objective, bound = float(summary["objective"]), float(summary["best_bound"])
    return abs(objective - bound) / max(1.0, abs(objective))


if __name__ == "__main__":
    print(relative_gap("CpSolverResponse summary:\nstatus: FEASIBLE\nobjective: 200\nbest_bound: 210\n"))
