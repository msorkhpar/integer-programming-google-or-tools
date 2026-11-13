"""Lesson 4.4.4: GridCap medium's multi-period selection (lesson 6.4.1's model): HiGHS against CP-SAT.

GridCap is a fictional utility's portfolio. The model is written once and built twice, in MathOpt
and in CP-SAT. Every run has a deterministic work limit and repeats exactly; each is run twice.
"""

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import groups_of, solve_highs

NODE_LIMIT = 2_000
DETERMINISTIC_TIME = 10


def build(portfolio, api: str):
    """Start-year binaries x[i, t], once/must rows, alternatives, parents with lags, yearly budgets."""
    by_id = {p.project_id: p for p in portfolio.projects}
    if api == "mathopt":
        model = mathopt.Model(name="multi-period")
        new_bool, add = (lambda name: model.add_binary_variable(name=name)), model.add_linear_constraint
    else:
        model = cp_model.CpModel()
        new_bool, add = model.new_bool_var, model.add
    x = {(p.project_id, t): new_bool(f"x_{p.project_id}_{t}") for p in portfolio.projects for t in p.starts()}

    def started(i):
        return sum(x[i, t] for t in by_id[i].starts())

    for p in portfolio.projects:
        add(started(p.project_id) == 1) if p.must_do else add(started(p.project_id) <= 1)
    for members in groups_of(portfolio).values():
        add(sum(started(i) for i in members) <= 1)
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                add(sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[c.parent, s] for s in parent.starts() if s <= t - c.parent_lag))
    for y in portfolio.years:
        add(sum(p.spend(t)[y] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()
                if y in p.spend(t)) <= portfolio.budget[y])
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return model, x


def with_highs(portfolio) -> tuple[str, float, float]:
    model, _ = build(portfolio, "mathopt")
    result = solve_highs(model, mathopt.SolveParameters(node_limit=NODE_LIMIT, relative_gap_tolerance=0.0))
    return result.termination.reason.name, result.objective_value(), result.termination.objective_bounds.dual_bound


def with_cpsat(portfolio, workers: int) -> tuple[str, float, float]:
    model, _ = build(portfolio, "cpsat")
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = workers
    solver.parameters.interleave_search = workers > 1      # a deterministic portfolio (lesson 4.6.3)
    solver.parameters.max_deterministic_time = DETERMINISTIC_TIME
    status = solver.solve(model)
    return solver.status_name(status), solver.objective_value, solver.best_objective_bound


medium = generate("medium")
model, x = build(medium, "cpsat")
print(f"GridCap medium: {len(medium.projects)} projects, {len(x)} start variables, {len(medium.years)} years")
print(f"{'solver':22} {'status':9} {'best plan':>10} {'bound':>10} {'gap':>6}  repeats")
for name, solve in (("HiGHS", with_highs),
                    ("CP-SAT, 1 worker", lambda p: with_cpsat(p, 1)),
                    ("CP-SAT, 8 interleaved", lambda p: with_cpsat(p, 8))):
    first, second = solve(medium), solve(medium)
    status, value, bound = first
    print(f"{name:22} {status:9} {value:>10,.0f} {bound:>10,.0f} {(bound - value) / value:>6.2%}  {first == second}")
