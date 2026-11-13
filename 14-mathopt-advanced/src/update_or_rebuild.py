"""Which edits each solver applies in place through an IncrementalSolver, and which make it start over.

IncrementalSolver.solve() (ortools/math_opt/python/solve.py) sends the edits since the last solve
to the solver it holds. If the solver cannot apply them, MathOpt silently builds a new solver from
the whole model. The new one is a different object, so comparing the held object before and after
a solve tells the two apart. `_proto_solver` is a private attribute: this is a diagnostic for
learning, not something to rely on in production code.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, quiet

small = generate("small")


def edits(pm):
    """Each edit is applied, then solved, on top of the ones before it."""
    yield "budget bound", lambda: setattr(pm.budget[2029], "upper_bound", 0.9 * small.budget[2029])
    yield "objective coef", lambda: pm.model.objective.set_linear_coefficient(pm.x["P032", 2027], 1000)
    yield "new row", lambda: pm.model.add_linear_constraint(pm.started("P030") + pm.started("P036") <= 1,
                                                            name="one_of_two")
    yield "delete row", lambda: pm.model.delete_linear_constraint(pm.budget[2031])
    yield "new variable", lambda: pm.model.add_binary_variable(name="spare")
    yield "integer -> continuous", lambda: setattr(pm.x["P001", 2028], "integer", False)


for solver_type in (mathopt.SolverType.GSCIP, mathopt.SolverType.HIGHS, mathopt.SolverType.CP_SAT):
    pm = build(small)
    report = []
    with quiet(), mathopt.IncrementalSolver(pm.model, solver_type) as solver:
        solver.solve()
        for name, apply in edits(pm):
            held = solver._proto_solver                       # private: diagnostic only
            apply()
            result = solver.solve()
            report.append(f"{name}: {'in place' if solver._proto_solver is held else 'REBUILT'}")
    print(f"{solver_type.name:6} final NPV {result.objective_value():,.0f} | " + ", ".join(report))
