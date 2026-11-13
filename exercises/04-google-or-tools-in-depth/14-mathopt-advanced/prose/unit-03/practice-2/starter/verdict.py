from __future__ import annotations


def hint_verdict(solver: str, log: list[str]) -> str:
    """accepted, partial, repairing, rejected or unknown, from a solver's log lines."""
    # TODO: the table's lines for this solver, in the table's order.
    return ""


if __name__ == "__main__":
    print(hint_verdict("HIGHS", ["MIP start solution is feasible, objective value is 90"]))
