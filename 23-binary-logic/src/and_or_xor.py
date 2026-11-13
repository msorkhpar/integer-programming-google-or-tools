"""Lesson 6.1.2: AND, OR and XOR as a new binary z, pinned from both sides.

For each (a, b) the program lists the values of z the rows allow: with all rows, with only the
rows that push z down, and with only the rows that push z up.
"""

from selection_model import allowed_values

GATES = {
    "z = a AND b": {"down": lambda m, v: (m.add_linear_constraint(v["z"] <= v["a"]),
                                          m.add_linear_constraint(v["z"] <= v["b"])),
                    "up": lambda m, v: m.add_linear_constraint(v["z"] >= v["a"] + v["b"] - 1)},
    "z = a OR b": {"down": lambda m, v: m.add_linear_constraint(v["z"] <= v["a"] + v["b"]),
                   "up": lambda m, v: (m.add_linear_constraint(v["z"] >= v["a"]),
                                       m.add_linear_constraint(v["z"] >= v["b"]))},
    "z = a XOR b": {"down": lambda m, v: (m.add_linear_constraint(v["z"] <= v["a"] + v["b"]),
                                          m.add_linear_constraint(v["z"] <= 2 - v["a"] - v["b"])),
                    "up": lambda m, v: (m.add_linear_constraint(v["z"] >= v["a"] - v["b"]),
                                        m.add_linear_constraint(v["z"] >= v["b"] - v["a"]))},
}


def z_values(rows, a: int, b: int) -> str:
    allowed = allowed_values(rows, ("a", "b", "z"))
    return " ".join(str(z) for (x, y, z) in allowed if (x, y) == (a, b)) or "none"


for gate, sides in GATES.items():
    print(f"{gate:12} a b | all rows | 'down' rows only | 'up' rows only")
    both = lambda m, v, s=sides: (s["down"](m, v), s["up"](m, v))
    for a in (0, 1):
        for b in (0, 1):
            print(f"{'':12} {a} {b} | {z_values(both, a, b):8} | {z_values(sides['down'], a, b):16} | "
                  f"{z_values(sides['up'], a, b)}")
