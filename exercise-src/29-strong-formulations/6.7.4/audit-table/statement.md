A modeling team wants the audit of the lesson as a reusable function, so that every reformulation
proposal arrives with the same table. Each formulation is given as a function `build(integer)` that
returns the model as a MILP (`integer=True`) or as its LP relaxation (`integer=False`); the first one
given is the model as inherited.

Write `audit(variants, optimum)` in `audit.py`. It returns one dictionary per formulation, in the
order given, with the keys

- `name`, `variables` and `rows`: the formulation's name and size;
- `lp`: its LP bound (GLOP is fine);
- `root`: HiGHS's bound after its root node, read the way the lesson read it;
- `closed`: the share of the **inherited** formulation's gap to `optimum` that this formulation's LP
  bound closes. If the inherited LP bound already equals `optimum`, there is no gap to close: the
  reference then reports `closed` as 1.0 on every line, instead of dividing by zero.

Before coding, write the formula for `closed` with the inherited LP bound, this formulation's LP
bound and the optimum, and work out its value for the inherited line itself and for a formulation
whose LP bound equals the optimum.

The tests audit three formulations of a three-item rule, small enough to check every number by
hand. About fifteen lines.
