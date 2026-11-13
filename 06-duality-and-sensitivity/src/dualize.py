"""Write the dual of any maximization LP whose variables are all >= 0 (lessons 2.3.1 and 2.3.2)."""

import math

from ortools.math_opt.python import mathopt


def dualize(primal: mathopt.Model) -> tuple[mathopt.Model, dict]:
    """The dual LP, and its price variable for each primal row (keyed by the row's name)."""
    if not primal.objective.is_maximize:
        raise ValueError("write the primal as a maximization")
    dual = mathopt.Model(name=f"dual of {primal.name}")
    price, rhs = {}, {}
    for row in primal.linear_constraints():
        lo, hi = row.lower_bound, row.upper_bound
        if lo == hi:                                    # == row: the price may have either sign
            price[row.name] = dual.add_variable(lb=-math.inf, ub=math.inf, name=f"y_{row.name}")
            rhs[row.name] = hi
        elif lo == -math.inf:                           # <= row: the price is >= 0
            price[row.name] = dual.add_variable(lb=0, name=f"y_{row.name}")
            rhs[row.name] = hi
        elif hi == math.inf:                            # >= row: the price is <= 0
            price[row.name] = dual.add_variable(lb=-math.inf, ub=0, name=f"y_{row.name}")
            rhs[row.name] = lo
        else:
            raise ValueError(f"{row.name}: split a two-sided row into a <= row and a >= row")
    for var in primal.variables():
        if var.lower_bound != 0 or var.upper_bound != math.inf:
            raise ValueError(f"{var.name}: write every bound other than >= 0 as a row")
        column = sum(row.get_coefficient(var) * price[row.name] for row in primal.column_nonzeros(var))
        dual.add_linear_constraint(column >= primal.objective.get_linear_coefficient(var), name=f"cover_{var.name}")
    dual.minimize(sum(rhs[name] * y for name, y in price.items()))
    return dual, price
