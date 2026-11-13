from __future__ import annotations

from ortools.sat.python import cp_model


def named_conflict(nurses: list[str], need: dict, max_shifts: dict, days_off: list) -> list[str] | None:
    """The roster rules CP-SAT names as clashing (sorted), or None if a roster exists."""
    model = cp_model.CpModel()
    days = sorted(need)
    works = {(n, d): model.new_bool_var(f"works_{n}_{d}") for n in nurses for d in days}
    flags = {}

    def rule(name, constraint):
        flags[name] = model.new_bool_var(f"flag_{name}")
        constraint.only_enforce_if(flags[name])

    for d in days:
        rule(f"cover_{d}", model.add(sum(works[n, d] for n in nurses) >= need[d]))
    for n in nurses:
        rule(f"max_{n}", model.add(sum(works[n, d] for d in days) <= max_shifts[n]))
    for n, d in days_off:
        if d not in need:
            continue                                   # not a roster day: nothing to forbid, no rule
        rule(f"off_{n}_{d}", model.add(works[n, d] == 0))
    model.add_assumptions(list(flags.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    if solver.solve(model) != cp_model.INFEASIBLE:
        return None
    by_index = {flag.index: name for name, flag in flags.items()}
    return sorted(by_index[i] for i in solver.sufficient_assumptions_for_infeasibility())


if __name__ == "__main__":
    print(named_conflict(["Ana", "Ben"], {1: 3}, {"Ana": 5, "Ben": 5}, []))
