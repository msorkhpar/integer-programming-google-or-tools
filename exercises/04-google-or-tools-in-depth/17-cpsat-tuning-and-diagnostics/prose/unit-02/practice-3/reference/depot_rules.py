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
    expr = sum(coef * var[name] for name, coef in rule.terms.items())
    return model.add(expr <= rule.rhs) if rule.sense == "<=" else model.add(expr >= rule.rhs)


def clashing_rules(variables: dict[str, tuple[int, int]], rules: list[Rule]) -> list[str]:
    """Given: the rules CP-SAT names as sufficient for infeasibility; [] if they can all hold."""
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


def feasible(variables: dict[str, tuple[int, int]], rules: list[Rule]) -> bool:
    """Given: can these rules all hold at once?"""
    model = cp_model.CpModel()
    var = {name: model.new_int_var(low, high, name) for name, (low, high) in variables.items()}
    for rule in rules:
        add_rule(model, var, rule)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    return solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def minimal_clash(variables: dict[str, tuple[int, int]], rules: list[Rule]) -> list[str]:
    """A clash from which no rule can be dropped without the rest becoming feasible; [] if none."""
    clash = clashing_rules(variables, rules)
    by_name = {r.name: r for r in rules}
    kept = list(clash)
    for name in clash:
        trial = [n for n in kept if n != name]
        if not feasible(variables, [by_name[n] for n in trial]):
            kept.remove(name)
    return kept


if __name__ == "__main__":
    crews = {"north": (2, 6)}
    print(minimal_clash(crews, [Rule("a", {"north": 1}, "<=", 3), Rule("b", {"north": 1}, ">=", 5)]))
