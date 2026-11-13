"""The activity rules of presolve on two small rows: fixing by activity, and coefficient tightening."""

from ortools.math_opt.python import mathopt

from presolve import BinaryModel, Row, activity, presolve, tighten

# Three projects, one budget of 8 ($M); PA is a must-do.
budget = BinaryModel({"PA": 7, "PB": 5, "PC": 4},
                     {"budget": Row({"PA": 6, "PB": 4, "PC": 3}, "<=", 8),
                      "must_PA": Row({"PA": 1}, "==", 1)})
least, most = activity(budget.rows["budget"], budget.lo, budget.hi)
print(f"budget row 6 PA + 4 PB + 3 PC <= 8: least activity {least}, most {most}")
done = presolve(budget)
for line in done.log:
    print(f"  {line}")
print(f"  fixed: {done.fixed}")

# Coefficient tightening: 5 PA + 2 PB + 2 PC <= 6.
row = Row({"PA": 5, "PB": 2, "PC": 2}, "<=", 6)
lo, hi = dict.fromkeys(row.coefs, 0), dict.fromkeys(row.coefs, 1)
print("row 5 PA + 2 PB + 2 PC <= 6: most activity without PA is 4, so PA's 5 can drop by 6 - 4 = 2")
for j, old, new in tighten(row, lo, hi):
    print(f"  {j}: {old} -> {new}")
print(f"  tightened row: {row.coefs['PA']} PA + {row.coefs['PB']} PB + {row.coefs['PC']} PC <= {row.rhs}")


def lp_bound(coefs: dict[str, float], rhs: float) -> tuple[float, dict[str, float]]:
    model = mathopt.Model()
    x = {j: model.add_variable(lb=0, ub=1, name=j) for j in coefs}
    model.maximize(5 * x["PA"] + 3 * x["PB"] + 3 * x["PC"])
    model.add_linear_constraint(sum(a * x[j] for j, a in coefs.items()) <= rhs)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.objective_value(), {j: round(result.variable_values(v), 3) for j, v in x.items()}


print("objective max 5 PA + 3 PB + 3 PC; the best 0-1 plan is PB and PC, value 6")
for label, coefs, rhs in (("original row: ", {"PA": 5, "PB": 2, "PC": 2}, 6), ("tightened row:", row.coefs, row.rhs)):
    bound, x = lp_bound(coefs, rhs)
    print(f"  LP bound, {label} {bound:.1f} at " + ", ".join(f"{j} = {v:g}" for j, v in x.items()))
