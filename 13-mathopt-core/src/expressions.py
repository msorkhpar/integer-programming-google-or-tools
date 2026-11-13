"""Linear expressions: built with + and *, kept as a tree, flattened and evaluated on demand."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="expressions")
x = model.add_binary_variable(name="x")
y = model.add_variable(lb=0, ub=2.5, name="y")
z = model.add_integer_variable(lb=0, ub=4, name="z")

expr = 2 * x + 3 * y + x + 5
print(type(expr).__name__, "->", expr)

flat = mathopt.as_flat_linear_expression(expr)
print(type(flat).__name__, "offset", flat.offset, {v.name: c for v, c in flat.terms.items()})

print("value at x=1, y=0.5:", mathopt.evaluate_expression(expr, {x: 1, y: 0.5}))

total = sum([x, y, z])                  # Python's sum: a nested LinearSum per addition, starting at 0
quick = mathopt.fast_sum([x, y, z])     # one flat LinearSum over the whole iterable
print("sum:", total, "| fast_sum:", quick)
