"""Walk the budget split's vertices with the tableau simplex, printing every pivot."""

from simplex import entering, fmt, leaving, pivot, show, solve, tableau
from split_lp import NAMES, ROWS, VALUE

A = [list(a) for a, _ in ROWS.values()]
b = [rhs for _, rhs in ROWS.values()]
names = list(NAMES) + [f"s_{label}" for label in ROWS]
T = tableau(A, b, VALUE)
basis = list(range(len(NAMES), len(names)))
show(T, names, basis)
while (k := entering(T)) is not None:
    print(f"\nentering {names[k]}: its objective-row entry is {fmt(T[-1][k])}")
    for i in range(len(A)):
        a = T[i][k]
        test = f"{fmt(T[i][-1])} divided by {fmt(a)} is {fmt(T[i][-1] / a)}" if a > 1e-9 else f"entry {fmt(a)}, sets no limit"
        print(f"  ratio test, row {names[basis[i]]}: {test}")
    r = leaving(T, k)
    print(f"leaving {names[basis[r]]}")
    T = pivot(T, r, k)
    basis[r] = k
    show(T, names, basis)
print("\nno negative entry left in the objective row: optimal")

result = solve(A, b, VALUE, names)
for entered, left, step, x, value in result.steps:
    print(f"{entered} enters, {left} leaves, step {step:g}: vertex ({x[0]:g}, {x[1]:g}), value {value:g}")
print(f"{result.status}: d = {result.x[0]:g}, t = {result.x[1]:g}, value {result.value:g}")
