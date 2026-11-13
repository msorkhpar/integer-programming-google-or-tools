# 5.3. gurobipy

Gurobi through its own Python interface. GridCap's selection and timing models are ported from
MathOpt row for row and as matrices, and Gurobi finds the same optima. Then the parts of gurobipy a
MathOpt user reaches for: attributes for everything a solve reports, LP duals with their ranges and
what a MIP offers instead, `computeIIS` and `feasRelax` on an infeasible scenario, several objectives
with `setObjectiveN`, and piecewise-linear curves with `addGenConstrPWL`. The last lesson covers the
licenses: what each one allows, where each can run, and how to keep license details out of every
output.

Every program here needs your own Gurobi license (lesson 5.3.4 says how to give the course's runner
one); the practices need none. MathOpt's `SolverType.GUROBI` does not run in the course's runner
(lesson 4.2.3), so this module uses gurobipy directly. GridCap is a fictional utility.

Two models here come from section 6, which the course reaches later: the timing model of lesson
6.4.1 (lesson 5.3.1 on; section 4 used it too, from lesson 4.3.1) and the credit-line curve of
lesson 6.6.2 (lesson 5.3.3). You do not need to have read them. Each lesson restates its model in
full, and where it compares Gurobi with "lesson 6.4.1's optimum" or "lesson 6.6.2's optimum", it
shows the output that lesson recorded on the page.

## Contents

1. [Models, attributes and the matrix API](README_5.3.1.md)
2. [Duals, reduced costs and sensitivity attributes](README_5.3.2.md)
3. [`computeIIS`, `feasRelax` and `setObjectiveN`](README_5.3.3.md)
4. [Licenses: size-limited, academic, and cloud/container (WLS)](README_5.3.4.md)
