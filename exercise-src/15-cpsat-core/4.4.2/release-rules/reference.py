from __future__ import annotations

from ortools.sat.python import cp_model


def add_rules(model: cp_model.CpModel, x: dict, requires: list[tuple[str, str]], excludes: list[tuple[str, str]],
              needs_one_of: list[tuple[str, list[str]]], bundles: list[tuple[str, str]]) -> None:
    """The release rules, one CP-SAT logic constraint each."""
    for a, b in requires:
        model.add_implication(x[a], x[b])
    for a, b in excludes:
        model.add_at_most_one(x[a], x[b])
    for a, options in needs_one_of:
        model.add_bool_or(x[o] for o in options).only_enforce_if(x[a])
    for a, b in bundles:
        model.add(x[a] == x[b])


if __name__ == "__main__":
    model = cp_model.CpModel()
    x = {f: model.new_bool_var(f) for f in ("sso", "audit", "export")}
    add_rules(model, x, [("audit", "sso")], [], [("export", ["sso", "audit"])], [])
    solver = cp_model.CpSolver()
    print(solver.status_name(solver.solve(model)))
