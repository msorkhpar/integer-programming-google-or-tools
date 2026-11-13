"""Mock 2's trap about CP-SAT assumptions: what the Python API calls them, and what it returns.

Five rules on four jobs, each rule guarded by a flag (lesson 4.6.2). Three of the rules cannot hold
together. The solver names a set of flags that is sufficient for the conflict; a deletion filter
(lesson 9.1.3) then removes every flag the conflict does not need.
"""

from __future__ import annotations

from ortools.sat.python import cp_model


def build(active: list[str]) -> tuple[cp_model.CpModel, dict]:
    model = cp_model.CpModel()
    job = {j: model.new_bool_var(j) for j in ("J1", "J2", "J3", "J4")}
    flag = {name: model.new_bool_var(f"flag_{name}") for name in active}
    rules = {
        "must_J1": lambda: model.add(job["J1"] == 1),
        "must_J2": lambda: model.add(job["J2"] == 1),
        "crew_cap": lambda: model.add(job["J1"] + job["J2"] + job["J3"] <= 1),
        "must_J4": lambda: model.add(job["J4"] == 1),
        "pair_J3_J4": lambda: model.add(job["J3"] + job["J4"] >= 1),
    }
    for name in active:
        rules[name]().only_enforce_if(flag[name])
    model.add_assumptions(list(flag.values()))
    return model, flag


def solve(active: list[str]) -> tuple[int, list[str]]:
    model, flag = build(active)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1                # assumptions are reported with one worker
    status = solver.solve(model)
    named = []
    if status == cp_model.INFEASIBLE:
        by_index = {f.index: name for name, f in flag.items()}
        named = sorted(by_index[i] for i in solver.sufficient_assumptions_for_infeasibility())
    return status, named


def deletion_filter(rules: list[str]) -> list[str]:
    keep = list(rules)
    for name in rules:
        trial = [r for r in keep if r != name]
        if solve(trial)[0] == cp_model.INFEASIBLE:   # still infeasible without it: drop it
            keep = trial
    return keep


def main() -> None:
    print("CpSolver has SolveWithAssumptions:", hasattr(cp_model.CpSolver, "SolveWithAssumptions"))
    print("CpModel has add_assumptions:", hasattr(cp_model.CpModel, "add_assumptions"))
    print("CpSolver has sufficient_assumptions_for_infeasibility:",
          hasattr(cp_model.CpSolver, "sufficient_assumptions_for_infeasibility"))
    rules = ["must_J1", "must_J2", "crew_cap", "must_J4", "pair_J3_J4"]
    status, named = solve(rules)
    print(f"status {cp_model.CpSolver().status_name(status)}; flags named: {', '.join(named)}")
    print(f"after a deletion filter: {', '.join(deletion_filter(named))}")


if __name__ == "__main__":
    main()
