from __future__ import annotations

from ortools.math_opt.python import mathopt

# orders[order][option] = pallets that option unloads at dock D (0 if it uses another dock)
Orders = dict[str, dict[str, int]]


def choice_variables(model: mathopt.Model, orders: Orders) -> dict:
    """choose[order, option] = 1: the order ships this week by that option. At most one per order."""
    choose = {(o, opt): model.add_binary_variable(name=f"choose_{o}_{opt}") for o, options in orders.items()
              for opt in options}
    for o, options in orders.items():
        model.add_linear_constraint(sum(choose[o, opt] for opt in options) <= 1, name=f"one_{o}")
    return choose


def dock_m(orders: Orders, capacity: int) -> int:
    """The smallest M for dock D's row that the one-option-per-order rows justify."""
    # TODO
    return 0


def add_dock_row(model: mathopt.Model, choose: dict, orders: Orders, capacity: int,
                 overflow: mathopt.Variable) -> None:
    """Pallets unloaded at dock D stay within `capacity`, unless the overflow yard is opened."""
    # TODO: your row.
    return None


if __name__ == "__main__":
    orders = {"O1": {"small": 4, "big": 9}, "O2": {"small": 3, "big": 7}}
    print("M =", dock_m(orders, 10))
