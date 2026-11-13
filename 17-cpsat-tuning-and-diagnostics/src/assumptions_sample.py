"""Lesson 4.6.2: assumptions and the sufficient set behind an INFEASIBLE.

The first model is adapted from the OR-Tools example `assumptions_sample_sat.py`
(https://github.com/google/or-tools/blob/stable/ortools/sat/samples/assumptions_sample_sat.py,
Apache-2.0): three rules in a cycle, each guarded by a flag. The second adds rules that do not
clash, to see which flags the solver names.
"""

from ortools.sat.python import cp_model

# Three rules that cannot hold together: x > y, y > z and z > x.
model = cp_model.CpModel()
x = model.new_int_var(0, 10, "x")
y = model.new_int_var(0, 10, "y")
z = model.new_int_var(0, 10, "z")
a = model.new_bool_var("a")
b = model.new_bool_var("b")
c = model.new_bool_var("c")
model.add(x > y).only_enforce_if(a)
model.add(y > z).only_enforce_if(b)
model.add(z > x).only_enforce_if(c)
model.add_assumptions([a, b, c])

solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
status = solver.solve(model)
print(f"cycle: {solver.status_name(status)}, sufficient assumptions "
      f"{solver.sufficient_assumptions_for_infeasibility()}")
print("variable indices:", {v.name: v.index for v in (x, y, z, a, b, c)})

# Four flagged rules; only "at least 5" and "at most 3" clash.
model = cp_model.CpModel()
crews = model.new_int_var(0, 10, "crews")
trucks = model.new_int_var(0, 10, "trucks")
flags = {name: model.new_bool_var(name) for name in ("trucks_min", "crews_min", "crews_max", "trucks_max")}
model.add(trucks >= 1).only_enforce_if(flags["trucks_min"])
model.add(crews >= 5).only_enforce_if(flags["crews_min"])
model.add(crews <= 3).only_enforce_if(flags["crews_max"])
model.add(trucks <= 5).only_enforce_if(flags["trucks_max"])
model.add_assumptions(list(flags.values()))

solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
status = solver.solve(model)
by_index = {flag.index: name for name, flag in flags.items()}
print(f"four rules: {solver.status_name(status)}, sufficient assumptions "
      f"{[by_index[i] for i in solver.sufficient_assumptions_for_infeasibility()]}")
