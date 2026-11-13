"""One GridCap model, built once, handed to every solver OR-Tools 9.15 ships, as an LP and as a MILP."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve

S = mathopt.SolverType
small = generate("small")
models = {"LP": build(small, integer=False), "MILP": build(small)}


def attempt(kind: str, solver: mathopt.SolverType) -> str:
    sel = models[kind]
    try:
        result = solve(sel.model, solver)
    except Exception as error:          # a refusal; lesson 4.2.4 reads its message properly
        return "refused: " + str(error.__context__ or error).split(" [")[0]
    funded = plan(sel, result)
    extras = [name for name, has in (("duals", result.has_dual_feasible_solution()),
                                      ("basis", result.has_basis())) if has]
    count = f"  funded {len(funded)}" if kind == "MILP" else ""
    return (f"{result.termination.reason.name} {result.objective_value():,.1f}"
            f"{count}  {' + '.join(extras) or 'no duals'}")


for kind in models:
    print(kind)
    for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
        print(f"  {solver.name:<7} {attempt(kind, solver)}")

lp, milp = models["LP"], models["MILP"]
plans = {solver.name: plan(milp, solve(milp.model, solver)) for solver in (S.HIGHS, S.GSCIP, S.CP_SAT)}
print("the three MILP solvers fund the same projects:", len({tuple(p) for p in plans.values()}) == 1)

print("compiled into this OR-Tools:")
for solver in S:
    if solver in (S.GUROBI,):
        continue
    try:
        mathopt.solve(mathopt.Model(), solver)
        print(f"  {solver.name:<9} yes")
    except Exception as error:
        print(f"  {solver.name:<9} no: {str(error.__context__ or error).split(',')[0]}")
