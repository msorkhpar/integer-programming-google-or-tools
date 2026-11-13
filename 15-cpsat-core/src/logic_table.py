"""Lesson 4.4.2: each of CP-SAT's logic constraints, and the 0/1 assignments it allows."""

from cpsat_models import allowed_assignments

CONSTRAINTS = [
    # name, variables, the constraint
    ("add_bool_or(a, b)", "ab", lambda m, v: m.add_bool_or(v["a"], v["b"])),
    ("add_bool_and(a, ~b)", "ab", lambda m, v: m.add_bool_and(v["a"], ~v["b"])),
    ("add_implication(a, b)", "ab", lambda m, v: m.add_implication(v["a"], v["b"])),
    ("add_at_most_one(a, b, c)", "abc", lambda m, v: m.add_at_most_one(v["a"], v["b"], v["c"])),
    ("add_exactly_one(a, b, c)", "abc", lambda m, v: m.add_exactly_one(v["a"], v["b"], v["c"])),
    ("add_bool_xor(a, b)", "ab", lambda m, v: m.add_bool_xor(v["a"], v["b"])),
    ("add_bool_or(~a, ~b, c)", "abc", lambda m, v: m.add_bool_or(~v["a"], ~v["b"], v["c"])),
    ("add_bool_or(b, c).only_enforce_if(a)", "abc",
     lambda m, v: m.add_bool_or(v["b"], v["c"]).only_enforce_if(v["a"])),
    ("add(a == b)", "ab", lambda m, v: m.add(v["a"] == v["b"])),
]

print(f"{'constraint':38} allows")
for name, names, rows in CONSTRAINTS:
    print(f"{name:38} {' '.join(allowed_assignments(rows, names))}")
