"""Reading a PuLP 3.3 result: the return code, the two statuses, and values that are None."""

import warnings
from dataclasses import replace

import pulp

from gridcap import generate
from legacy_selection import solve_legacy

warnings.simplefilter("ignore", DeprecationWarning)
small = generate("small")

# 1. A budget too small for the must-do projects: no plan exists.
must = sum(p.capex for p in small.projects if p.must_do)
tight = replace(small, capital_budget=must - 1000)
status, total, funded, prob = solve_legacy(tight)
code = prob.status
print(f"must-do capex ${must:,}k, budget ${tight.capital_budget:,}k")
print(f"solve() returned {code} ({pulp.LpStatus[code]}); `if prob.solve():` takes the branch: {bool(code)}")
print(f"the legacy script still reports: value ${total:,.2f}k, funded {funded}")
odd = {v.name: round(v.varValue, 3) for v in prob.variables() if v.varValue not in (0.0, 1.0)}
print("  binary variables left holding a value that is not 0 or 1:", odd)


# 2. A variable that never entered the problem has no value at all.
x = pulp.LpVariable.dicts("x", ["P001", "P002", "P003"], cat="Binary")
on_hold = {"P003"}                                    # left out of every row and of the objective
hold = pulp.LpProblem("on_hold", pulp.LpMaximize)
hold += pulp.lpSum((i + 1) * x[pid] for i, pid in enumerate(x) if pid not in on_hold), "value"
hold += pulp.lpSum(x[pid] for pid in x if pid not in on_hold) <= 1, "one"
hold.solve(pulp.PULP_CBC_CMD(msg=0))
print("after the solve:", {pid: v.varValue for pid, v in x.items()})
try:
    print([pid for pid in x if pulp.value(x[pid]) > 0.5])
except TypeError as error:
    print("value(x) > 0.5 raised TypeError:", error)


# 3. A problem with no objective has prob.objective None, and value(None) raises.
check = pulp.LpProblem("feasibility_check", pulp.LpMinimize)
check += x["P001"] + x["P002"] >= 1, "cover"
check.solve(pulp.PULP_CBC_CMD(msg=0))
print("objective:", check.objective, "| status", pulp.LpStatus[check.status])
try:
    print(pulp.value(check.objective))
except AttributeError as error:
    print("value(prob.objective) raised AttributeError:", error)


# A reader that refuses every one of these instead of reporting a plan.
class NoPlan(RuntimeError):
    pass


def read_plan(prob, x, proved=True):
    """Funded ids, only from a solve that ended with a solution (proved optimal, unless proved=False)."""
    wanted = {pulp.LpSolutionOptimal} if proved else {pulp.LpSolutionOptimal, pulp.LpSolutionIntegerFeasible}
    if prob.status != pulp.LpStatusOptimal or prob.sol_status not in wanted:
        raise NoPlan(f"status {pulp.LpStatus[prob.status]}, {pulp.LpSolution[prob.sol_status]}")
    missing = [key for key, var in x.items() if var.varValue is None]
    if missing:
        raise NoPlan(f"no value for {missing}: not in the problem")
    return [key for key, var in x.items() if var.varValue > 0.5]


for label, (p, variables) in {"infeasible budget": (prob, {v.name: v for v in prob.variables()}),
                              "project on hold": (hold, x)}.items():
    try:
        print(f"read_plan, {label}:", read_plan(p, variables))
    except NoPlan as error:
        print(f"read_plan, {label}: refused ({error})")
