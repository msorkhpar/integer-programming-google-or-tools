"""One GridCap solve, described by a config, returned as a run record: a manifest and the clock.

    python3 solve_once.py '{"size": "small", "objective": "npv", "order": "given", "solver": "highs", "params": {}}'

prints the record as one line of canonical JSON. Lessons 10.2.1 to 10.2.5 run it in a fresh process
per run (repeat.py and harness.py), so every run starts with its own hash seed, its own solver
libraries and its own thread settings. Run with no argument, it solves one default config and
prints a summary line.

Config keys: `size` (a GridCap size), `objective` ("npv" or "count"), `order` ("given", or "set":
the projects in the order of a Python set, the bug of lesson 10.2.1), `solver` ("highs", "scip",
"cpsat" or "gurobi") and `params`, in the solver's own names (see `PARAMS` below for MathOpt).
GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import datetime
import json
import sys
import time

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2
from ortools.sat.python import cp_model

from gridcap import generate
from manifest import canonical, versions
from plan_model import build, build_cpsat, digest, schedule, schedule_cpsat, solve_highs

SOLVERS = {"highs": mathopt.SolverType.HIGHS, "scip": mathopt.SolverType.GSCIP}


def mathopt_params(solver: str, params: dict) -> mathopt.SolveParameters:
    """MathOpt's common parameters by name; HiGHS's thread count goes in its own options (lesson 4.2.4)."""
    common = {k: v for k, v in params.items() if k != "highs_threads"}
    if "time_limit" in common:
        common["time_limit"] = datetime.timedelta(seconds=common["time_limit"])
    solve_params = mathopt.SolveParameters(**common)
    if "highs_threads" in params:
        solve_params.highs = highs_pb2.HighsOptionsProto(int_options={"threads": params["highs_threads"]})
    return solve_params


def result_of(status: str, objective, bound, starts: dict[str, int], stats: dict) -> dict:
    return {"status": status,
            "objective": None if objective is None else round(objective, 6),
            "bound": round(bound, 6),
            "plan_digest": digest(starts),
            "plan": sorted([pid, t] for pid, t in starts.items()),
            "stats": stats}


def solve_mathopt(config: dict, portfolio, order) -> dict:
    plan = build(portfolio, order, config["objective"])
    params = mathopt_params(config["solver"], config.get("params", {}))
    if config["solver"] == "highs":
        result = solve_highs(plan.model, params)
    else:
        result = mathopt.solve(plan.model, SOLVERS[config["solver"]], params=params)
    found = result.has_primal_feasible_solution()
    return result_of(result.termination.reason.name, result.objective_value() if found else None,
                     result.termination.objective_bounds.dual_bound,
                     schedule(plan, result) if found else {},
                     {"nodes": result.solve_stats.node_count,
                      "simplex_iterations": result.solve_stats.simplex_iterations})


def solve_cpsat(config: dict, portfolio, order) -> dict:
    plan = build_cpsat(portfolio, order, config["objective"])
    solver = cp_model.CpSolver()
    for name, value in config.get("params", {}).items():
        setattr(solver.parameters, name, value)
    status = solver.solve(plan.model)
    found = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    return result_of(solver.status_name(status), solver.objective_value if found else None,
                     solver.best_objective_bound, schedule_cpsat(plan, solver) if found else {},
                     {"branches": solver.num_branches, "conflicts": solver.num_conflicts,
                      "deterministic_time": round(solver.deterministic_time, 4)})


def solve_gurobi(config: dict, portfolio, order) -> dict:
    import gurobipy as gp

    from grb_plan import build_gurobi, quiet_env

    try:
        env = quiet_env()
    except gp.GurobiError as error:                      # never print the message: it names the machine
        return {"status": f"NO_LICENSE (GurobiError {error.errno})"}
    model, x = build_gurobi(env, portfolio, order, config["objective"])
    for name, value in config.get("params", {}).items():
        model.setParam(name, value)
    model.optimize()
    found = model.SolCount > 0
    starts = {pid: t for (pid, t), v in x.items() if v.X > 0.5} if found else {}
    names = {getattr(gp.GRB.Status, n): n for n in dir(gp.GRB.Status) if n.isupper()}
    return result_of(names[model.Status], model.ObjVal if found else None, model.ObjBound, starts,
                     {"nodes": int(model.NodeCount), "simplex_iterations": int(model.IterCount),
                      "work": round(model.Work, 6), "fingerprint": model.Fingerprint})


def run(config: dict) -> dict:
    """Build and solve one config; return {"manifest": ..., "clock": ...}."""
    started = time.perf_counter()
    portfolio = generate(config["size"])
    order = list(set(portfolio.project_ids)) if config.get("order") == "set" else None
    solve = {"highs": solve_mathopt, "scip": solve_mathopt, "cpsat": solve_cpsat,
             "gurobi": solve_gurobi}[config["solver"]]
    result = solve(config, portfolio, order)
    manifest = {"inputs": {"snapshot": portfolio.content_hash(), "size": config["size"],
                           "objective": config["objective"], "order": config.get("order", "given")},
                "solver": {"name": config["solver"], "params": config.get("params", {})},
                "versions": versions(config["solver"]),
                "result": result}
    return {"manifest": manifest, "clock": {"wall_seconds": round(time.perf_counter() - started, 3)}}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(canonical(run(json.loads(sys.argv[1]))).decode("ascii"))
    else:
        record = run({"size": "small", "objective": "npv", "solver": "highs", "params": {}})
        result = record["manifest"]["result"]
        print(f"highs on small: {result['status']} {result['objective']:,.0f} plan {result['plan_digest']}")
