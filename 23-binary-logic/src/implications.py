"""Lesson 6.1.2: each implication between binaries is one linear row, checked against its truth table.

For every rule the program asks HiGHS which 0/1 assignments the row allows, and compares them with
the assignments the logic allows.
"""

import itertools

from selection_model import allowed_values

RULES = [
    # name, variables, the logic, the rows, the rows as text
    ("a -> b", "ab", lambda a, b: (not a) or b,
     lambda m, v: m.add_linear_constraint(v["a"] <= v["b"]), "x_a <= x_b"),
    ("a -> not b", "ab", lambda a, b: not (a and b),
     lambda m, v: m.add_linear_constraint(v["a"] + v["b"] <= 1), "x_a + x_b <= 1"),
    ("not a -> b", "ab", lambda a, b: a or b,
     lambda m, v: m.add_linear_constraint(v["a"] + v["b"] >= 1), "x_a + x_b >= 1"),
    ("(a and b) -> c", "abc", lambda a, b, c: not (a and b) or c,
     lambda m, v: m.add_linear_constraint(v["a"] + v["b"] - 1 <= v["c"]), "x_a + x_b - 1 <= x_c"),
    ("a -> (b or c)", "abc", lambda a, b, c: (not a) or b or c,
     lambda m, v: m.add_linear_constraint(v["a"] <= v["b"] + v["c"]), "x_a <= x_b + x_c"),
    ("(a or b) -> c", "abc", lambda a, b, c: not (a or b) or c,
     lambda m, v: (m.add_linear_constraint(v["a"] <= v["c"]), m.add_linear_constraint(v["b"] <= v["c"])),
     "x_a <= x_c, x_b <= x_c"),
    ("a -> b, reversed", "ab", lambda a, b: (not a) or b,
     lambda m, v: m.add_linear_constraint(v["a"] >= v["b"]), "x_a >= x_b"),
]

print(f"{'rule':18} {'row':24} {'assignments the row allows':34} logic")
for name, names, logic, rows, text in RULES:
    by_row = allowed_values(rows, tuple(names))
    by_logic = [vals for vals in itertools.product((0, 1), repeat=len(names)) if logic(*vals)]
    shown = " ".join("".join(map(str, vals)) for vals in by_row)
    print(f"{name:18} {text:24} {shown:34} {'same' if by_row == by_logic else 'DIFFERS'}")
