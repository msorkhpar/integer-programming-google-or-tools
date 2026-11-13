from __future__ import annotations

from ortools.math_opt.python import mathopt


def tighten(cost: dict, budget: int, hours: dict, need: dict) -> tuple[set, set]:
    """Inspections every allowed plan must include, and inspections no allowed plan can include.

    `hours[d][j]` is what inspection j gives district d, `need[d]` the hours district d must get.
    Each row is used on its own, and the pass repeats until nothing changes.
    """
    ones: set = set()
    zeros: set = set()
    changed = True
    while changed:
        changed = False
        for d, gives in hours.items():
            for j, h in gives.items():
                if j in ones or j in zeros or h <= 0:
                    continue
                most_without = sum(g for k, g in gives.items() if k not in zeros and k != j)
                if most_without < need[d]:               # the district cannot be covered without j
                    ones.add(j)
                    changed = True
        spent = sum(cost[j] for j in ones)
        for j in cost:
            if j not in ones and j not in zeros and spent + cost[j] > budget:
                zeros.add(j)                              # j does not fit next to what must be done
                changed = True
    return ones, zeros


def build(cost: dict, budget: int, hours: dict, need: dict, value: dict, *, integer: bool = True,
          fixings: tuple[set, set] | None = None) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="inspections")
    x = {j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{j}") for j in cost}
    model.add_linear_constraint(sum(cost[j] * x[j] for j in cost) <= budget, name="budget")
    for d, gives in hours.items():
        model.add_linear_constraint(sum(h * x[j] for j, h in gives.items()) >= need[d], name=f"cover_{d}")
    if fixings is not None:
        ones, zeros = fixings
        for j in ones:
            x[j].lower_bound = 1
        for j in zeros:
            x[j].upper_bound = 0
    model.maximize(sum(value[j] * x[j] for j in cost))
    return model, x


if __name__ == "__main__":
    print(tighten({"A": 3, "B": 2}, 4, {"north": {"A": 5, "B": 1}}, {"north": 4}))
