from __future__ import annotations


def hint_verdict(solver: str, log: list[str]) -> str:
    """accepted, partial, repairing, rejected or unknown, from a solver's log lines."""
    rules = {
        "HIGHS": [("Attempting to find feasible solution by solving MIP for user-supplied values", "partial"),
                  ("cannot yield feasible solution", "rejected"),
                  ("MIP start solution is feasible", "accepted")],
        "GSCIP": [("feasible solution given by solution candidate storage", "accepted")],
        "CP_SAT": [("The solution hint is complete and is feasible", "accepted"),
                   ("The solution hint is incomplete", "partial"),
                   ("The solution hint is complete, but it is infeasible", "repairing")],
    }
    for words, verdict in rules.get(solver, []):
        if any(words in line for line in log):
            return verdict
    return "unknown"


if __name__ == "__main__":
    print(hint_verdict("HIGHS", ["MIP start solution is feasible, objective value is 90"]))
