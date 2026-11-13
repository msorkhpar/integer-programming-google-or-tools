"""A Benders loop on GridCap small: the master picks the plan, one LP per year prices its crew work."""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, generate

from capital import EXACT, build, crew_use, schedule, solve_highs, value
from crew_costs import CONTRACT_PRICE, OVERTIME_PRICE, OVERTIME_SHARE, POOL, PROGRAMS, need_of, year_lp

TOL = 1e-6


def monolithic(portfolio: Portfolio):
    """The whole model in one MILP: start variables and every year's crew variables together."""
    cap = build(portfolio)
    use = crew_use(portfolio, cap.x)
    cost = mathopt.LinearExpression()
    for y in portfolio.years:
        hires = []
        for g in PROGRAMS:
            own = cap.model.add_variable(lb=0, ub=portfolio.crews[g, y], name=f"own_{g}_{y}")
            over = cap.model.add_variable(lb=0, ub=OVERTIME_SHARE * portfolio.crews[g, y], name=f"over_{g}_{y}")
            hire = cap.model.add_variable(lb=0, name=f"hire_{g}_{y}")
            cap.model.add_linear_constraint(own + over + hire >= use.get((g, y), 0), name=f"cover_{g}_{y}")
            cost += OVERTIME_PRICE * over + CONTRACT_PRICE[g] * hire
            hires.append(hire)
        cap.model.add_linear_constraint(sum(hires) <= POOL, name=f"pool_{y}")
    cap.model.maximize(cap.model.objective.as_linear_expression() - cost)
    return cap, solve_highs(cap.model, EXACT)


def cut_expression(result: mathopt.SolveResult, rows: dict, need: dict, crews: dict):
    """sum over rows of dual * bound, with each cover row's bound written as the master's
    expression need_g(x): the LP's dual bound, valid for every plan, exact at this one."""
    expr = mathopt.LinearExpression()
    for g in PROGRAMS:
        expr += result.dual_values(rows[f"cover_{g}"]) * need[g]
        expr += result.dual_values(rows[f"own_{g}"]) * crews[g]
        expr += result.dual_values(rows[f"over_{g}"]) * OVERTIME_SHARE * crews[g]
    return expr + result.dual_values(rows["pool"]) * POOL


def operating_cost(portfolio: Portfolio, plan: dict[str, int]) -> float | None:
    """The plan's crew cost: the sum of the yearly LPs, or None if some year cannot be covered."""
    need = need_of(portfolio, plan)
    total = 0.0
    for y in portfolio.years:
        m, _ = year_lp(portfolio, y, {g: need[g, y] for g in PROGRAMS})
        r = mathopt.solve(m, mathopt.SolverType.GLOP)
        if r.termination.reason != mathopt.TerminationReason.OPTIMAL:
            return None
        total += r.objective_value()
    return total


def benders(portfolio: Portfolio, *, verbose: bool = True, max_iterations: int = 100):
    cap = build(portfolio)                                     # the master: no crew rows at all
    theta = {y: cap.model.add_variable(lb=0, name=f"theta_{y}") for y in portfolio.years}
    cap.model.maximize(cap.model.objective.as_linear_expression() - sum(theta.values()))
    use = crew_use(portfolio, cap.x)
    best_value, best_plan, log = -float("inf"), None, []
    for k in range(1, max_iterations + 1):
        master = solve_highs(cap.model, EXACT)
        upper = master.objective_value()
        plan = schedule(cap, master)
        need = need_of(portfolio, plan)
        feas_cuts = opt_cuts = 0
        total = 0.0
        for y in portfolio.years:
            crews = {g: portfolio.crews[g, y] for g in PROGRAMS}
            need_x = {g: use.get((g, y), mathopt.LinearExpression()) for g in PROGRAMS}
            m, rows = year_lp(portfolio, y, {g: need[g, y] for g in PROGRAMS}, phase_one=True)
            short = mathopt.solve(m, mathopt.SolverType.GLOP)
            if short.objective_value() > TOL:                  # no crews can cover this year's work
                cap.model.add_linear_constraint(cut_expression(short, rows, need_x, crews) <= 0,
                                                name=f"feas_{y}_{k}")
                feas_cuts += 1
                total = None
                continue
            m, rows = year_lp(portfolio, y, {g: need[g, y] for g in PROGRAMS})
            sub = mathopt.solve(m, mathopt.SolverType.GLOP)
            if total is not None:
                total += sub.objective_value()
            if master.variable_values(theta[y]) < sub.objective_value() - TOL:
                cap.model.add_linear_constraint(theta[y] >= cut_expression(sub, rows, need_x, crews),
                                                name=f"opt_{y}_{k}")
                opt_cuts += 1
        if total is not None and value(portfolio, plan) - total > best_value:
            best_value, best_plan = value(portfolio, plan) - total, plan
        log.append((k, upper, best_value, feas_cuts, opt_cuts))
        if verbose:
            lower = f"{best_value:10,.2f}" if best_plan else "      none"
            print(f"iter {k:2}  master (upper) {upper:10,.2f}  best plan (lower) {lower}"
                  f"  cuts: feasibility {feas_cuts}, optimality {opt_cuts}")
        if feas_cuts + opt_cuts == 0:
            break
    return best_value, best_plan, log


if __name__ == "__main__":
    small = generate("small")
    best, plan, log = benders(small)
    cap, mono = monolithic(small)
    print(f"Benders: {best:,.2f} after {len(log)} master solves;  monolithic MILP: {mono.objective_value():,.2f}")
    print(f"same plan: {plan == schedule(cap, mono)}   NPV {value(small, plan):,}  crew cost {operating_cost(small, plan):,.2f}")
