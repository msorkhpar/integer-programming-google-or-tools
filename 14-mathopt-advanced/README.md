# 4.3. MathOpt Advanced

The parts of MathOpt beyond model, solve and result: indicator constraints written, read back and
refused; prioritized objectives with `add_auxiliary_objective`, and how to solve them where no solver
takes them; solution hints and the other fields of `ModelSolveParameters`; incremental solving, with
budget-cut scenarios answered on one model; and callbacks and `compute_infeasible_subsystem`, with an
infeasible subsystem found by hand. Each lesson checks, in the course's runner (OR-Tools 9.15), which
solvers accept the feature, and shows how to read the real reason when one refuses.

## Contents

1. [Indicator constraints](README_4.3.1.md)
2. [Prioritized objectives with `add_auxiliary_objective`](README_4.3.2.md)
3. [Solution hints and `ModelSolveParameters`](README_4.3.3.md)
4. [Incremental solving: edit the model, re-solve](README_4.3.4.md)
5. [Callbacks and `compute_infeasible_subsystem`](README_4.3.5.md)
