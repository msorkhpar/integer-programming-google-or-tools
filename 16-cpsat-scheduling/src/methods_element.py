"""Lesson 4.5.3: each Coast job picks a method, and Element reads its weeks and cost from lists.

One crew does the four Coast jobs one after another. The method index m_j selects
weeks_j = W_j[m_j] and cost_j = C_j[m_j], and the job's interval takes the variable size weeks_j.
GridCap is fictional, and so are the method data.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve

METHODS = ["manual", "mechanical", "aerial"]
# job -> (weeks by method, cost $k by method); a method a job cannot use is left out by its domain
DATA = {"P011": ([4, 2, 1], [60, 75, 110]),
        "P012": ([6, 3, 2], [90, 105, 160]),
        "P014": ([2, 1, 1], [30, 40, 55]),
        "P015": ([2, 1, 1], [35, 45, 70])}


def plan(deadline: int) -> None:
    model = cp_model.CpModel()
    method, weeks, cost, end, tasks = {}, {}, {}, {}, []
    for j, (w, c) in DATA.items():
        method[j] = model.new_int_var(0, len(METHODS) - 1, f"method_{j}")
        weeks[j] = model.new_int_var(min(w), max(w), f"weeks_{j}")
        cost[j] = model.new_int_var(min(c), max(c), f"cost_{j}")
        model.add_element(method[j], w, weeks[j])           # weeks_j = W_j[method_j]
        model.add_element(method[j], c, cost[j])            # cost_j  = C_j[method_j]
        start = model.new_int_var(0, deadline, f"start_{j}")
        end[j] = model.new_int_var(0, deadline, f"end_{j}")
        tasks.append(model.new_interval_var(start, weeks[j], end[j], f"work_{j}"))
    model.add_no_overlap(tasks)
    model.minimize(sum(cost.values()))
    solver, status = solve(model)
    print(f"deadline week {deadline}: {status}, cost ${solver.objective_value:.0f}k")
    for j in DATA:
        print(f"  {j} {METHODS[solver.value(method[j])]:<10} weeks {solver.value(weeks[j])}  ${solver.value(cost[j])}k")


if __name__ == "__main__":
    for deadline in (14, 8, 5):
        plan(deadline)
