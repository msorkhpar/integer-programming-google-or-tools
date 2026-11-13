"""Gomory fractional cuts by hand on a two-variable integer program, until the LP optimum is integer."""

from math import lcm

from tableau import build, frac, gomory, in_original_variables, show, solve, value_of

NAMES = ["d", "t"]
A = [[1, 1], [5, 9]]          # crews:  d + t <= 6;   money:  5d + 9t <= 45
b = [6, 45]
c = [5, 8]                    # value of a substation package, of a feeder package

for round_ in range(1, 10):
    T = solve(build(A, b, c, NAMES))
    point = [value_of(T, j) for j in range(len(c))]
    print(f"round {round_}: LP optimum d = {point[0]}, t = {point[1]}, value {T.rows[-1][-1]}")
    if all(v.denominator == 1 for v in point):
        print("  integer: done")
        break
    if round_ == 1:
        for line in show(T):
            print("  " + line)
    cuts = {}
    for i in range(len(T.basis)):
        if frac(T.rows[i][-1]):
            coef, rhs = gomory(T.rows[i])
            terms = " + ".join(f"{v}*{T.names[j]}" for j, v in enumerate(coef) if v)
            g, h = in_original_variables(coef, rhs, A, b)
            scale = lcm(*(v.denominator for v in g + [h]))
            cuts[i] = [int(v * scale) for v in g], int(h * scale)
            print(f"  row of {T.names[T.basis[i]]}: rhs {T.rows[i][-1]}, cut {terms} >= {rhs}; "
                  f"in d and t: {cuts[i][0][0]}*d + {cuts[i][0][1]}*t <= {cuts[i][1]}")
    r = max(cuts, key=lambda i: (frac(T.rows[i][-1]), -i))
    print(f"  add the cut of row {T.names[T.basis[r]]} (largest fractional part)")
    A.append(cuts[r][0])
    b.append(cuts[r][1])
