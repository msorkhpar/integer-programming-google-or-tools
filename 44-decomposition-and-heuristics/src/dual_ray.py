"""Does an infeasible LP come back with a Farkas certificate (a dual ray)? One year's crew LP, made
infeasible on purpose, asked of each LP solver MathOpt runs here."""

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="one infeasible year")
own = model.add_variable(lb=0, name="own")
hire = model.add_variable(lb=0, name="hire")
cover = model.add_linear_constraint(own + hire >= 10, name="cover")       # 10 crew-months of work
crews = model.add_linear_constraint(own <= 4, name="own")                 # 4 of our own
pool = model.add_linear_constraint(hire <= 3, name="pool")                # 3 contractors
model.minimize(25 * hire)

for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP):
    result = mathopt.solve(model, solver)
    line = f"{solver.name:5} {result.termination.reason.name:10} dual ray: {result.has_dual_ray()}"
    if result.has_dual_ray():
        ray = result.dual_rays[0].dual_values
        line += "  " + ", ".join(f"{row.name} {ray[row]:.1f}" for row in (cover, crews, pool))
    print(line)
