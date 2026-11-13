"""The LP bound of a one-budget model by hand: fund the must-dos, then the best NPV per dollar, then a fraction."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import broken_rows, lp_values

small = generate("small")


def greedy_bound(portfolio) -> tuple[float, list[tuple[str, float]]]:
    """Fill the budget by value per dollar and take a share of the first project that does not fit."""
    room = portfolio.capital_budget
    bound, taken = 0.0, []
    for p in portfolio.projects:                       # must-do projects are paid for first
        if p.must_do:
            room -= p.capex
            bound += p.value
            taken.append((p.project_id, 1.0))
    for p in sorted((p for p in portfolio.projects if not p.must_do), key=lambda p: p.value / p.capex, reverse=True):
        share = min(1.0, room / p.capex)
        room -= share * p.capex
        bound += share * p.value
        taken.append((p.project_id, share))
        if share < 1:
            break
    return bound, taken


def budget_only_lp(portfolio) -> float:
    """GLOP on the relaxation with only the budget and must-do rows: no parent, no alternative rows."""
    model = mathopt.Model(name="budget only")
    x = {p.project_id: model.add_variable(lb=0, ub=1, name=f"x_{p.project_id}") for p in portfolio.projects}
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


if __name__ == "__main__":
    bound, taken = greedy_bound(small)
    print(f"must-do first: {[pid for pid, _ in taken if small.project(pid).must_do]}")
    print("then by NPV per $k, the last three taken:")
    for pid, share in taken[-3:]:
        p = small.project(pid)
        print(f"  {pid}  NPV/capex {p.value / p.capex:.3f}  capex {p.capex:>5,}  share {share:.3f}")
    print(f"greedy bound                   {bound:,.2f}")
    print(f"GLOP, budget and must-do only  {budget_only_lp(small):,.2f}")
    print(f"GLOP, every rule               {lp_values(small)[0]:,.2f}")
    print(f"rows the greedy's whole projects break: {broken_rows(small, {pid for pid, s in taken if s == 1})}")
