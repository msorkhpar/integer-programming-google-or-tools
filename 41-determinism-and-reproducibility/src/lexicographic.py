"""Lesson 10.2.3: break the tie with a second real criterion, solved in two passes.

Pass 1 finds the most projects that fit; pass 2 holds that count and maximizes NPV; a third solve
with a no-good row checks that no other plan matches both. Each run is a fresh process with the
projects in a set's order (the bug of lesson 10.2.1), on HiGHS and on CP-SAT. GridCap is fictional.
"""

import json
import subprocess
import sys

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import generate
from repeat import child_env
from plan_model import build, build_cpsat, digest, schedule, schedule_cpsat, solve_highs

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def two_pass_highs(portfolio, order) -> dict:
    plan = build(portfolio, order, objective="count")
    most = round(solve_highs(plan.model, EXACT).objective_value())              # pass 1
    plan.model.add_linear_constraint(sum(plan.x.values()) >= most, name="keep_count")
    npv = sum(portfolio.project(i).npv[t] * v for (i, t), v in plan.x.items())
    plan.model.maximize(npv)                                                    # pass 2
    result = solve_highs(plan.model, EXACT)
    starts, best_npv = schedule(plan, result), round(result.objective_value())
    plan.model.add_linear_constraint(npv >= best_npv, name="keep_npv")          # is it unique?
    chosen = [plan.x[k] for k in starts.items()]
    plan.model.add_linear_constraint(sum(chosen) <= len(chosen) - 1, name="not_this_plan")
    other = solve_highs(plan.model, EXACT).termination.reason.name
    return {"count": most, "npv": best_npv, "plan": digest(starts), "another plan": other}


def two_pass_cpsat(portfolio, order) -> dict:
    plan = build_cpsat(portfolio, order, objective="count")
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(plan.model)
    most = round(solver.objective_value)
    plan.model.add(sum(plan.x.values()) >= most)
    plan.model.maximize(sum(portfolio.project(i).npv[t] * v for (i, t), v in plan.x.items()))
    solver.solve(plan.model)
    return {"count": most, "npv": round(solver.objective_value), "plan": digest(schedule_cpsat(plan, solver))}


if __name__ == "__main__" and len(sys.argv) > 1:          # one run, in a fresh process
    small = generate("small")
    order = list(set(small.project_ids))
    print(json.dumps((two_pass_highs if sys.argv[1] == "highs" else two_pass_cpsat)(small, order)))
elif __name__ == "__main__":
    for solver in ["highs", "cpsat"]:
        for seed in ["1", "2", "3", "4"]:
            env = child_env(seed)
            out = subprocess.run([sys.executable, __file__, solver], env=env, capture_output=True,
                                 text=True, check=True).stdout.strip()
            print(f"{solver:<5} hash seed {seed}: {out}")
