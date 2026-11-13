from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Rule:
    name: str
    terms: dict[str, int]       # variable name -> coefficient
    sense: str                  # "<=" or ">="
    rhs: int


def add_rule(model: cp_model.CpModel, var: dict[str, cp_model.IntVar], rule: Rule):
    """Given: add one rule as a linear constraint and return it."""
    expr = sum(coef * var[name] for name, coef in rule.terms.items())
    return model.add(expr <= rule.rhs) if rule.sense == "<=" else model.add(expr >= rule.rhs)


def clashing_rules(variables: dict[str, tuple[int, int]], rules: list[Rule]) -> list[str]:
    """Names of a set of rules that cannot hold together, as CP-SAT reports it; [] if all can."""
    model = cp_model.CpModel()
    var = {name: model.new_int_var(low, high, name) for name, (low, high) in variables.items()}
    flag = {}
    for rule in rules:
        flag[rule.name] = model.new_bool_var(f"flag_{rule.name}")
        add_rule(model, var, rule).only_enforce_if(flag[rule.name])
    model.add_assumptions(list(flag.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    if solver.solve(model) != cp_model.INFEASIBLE:
        return []
    by_index = {f.index: name for name, f in flag.items()}
    return sorted(by_index[i] for i in solver.sufficient_assumptions_for_infeasibility())


if __name__ == "__main__":
    crews = {"north": (2, 6), "south": (1, 6)}
    print(clashing_rules(crews, [Rule("pair_cap", {"north": 1, "south": 1}, "<=", 2)]))
