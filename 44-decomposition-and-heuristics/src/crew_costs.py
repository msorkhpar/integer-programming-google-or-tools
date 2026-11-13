"""The crew-cost layer of lessons 11.3.2: who does each year's crew work, and at what cost.

GridCap is fictional, and so is this layer: the overtime share, the prices and the contractor pool
are invented for the lesson. Each year, each program's crew-months of work are done by its own
crews (free: they are paid already), by overtime (up to a quarter of its crews), or by contractors
from one pool shared by all programs.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

PROGRAMS = ("transmission", "distribution", "vegetation")
OVERTIME_SHARE = 0.25                                       # overtime: at most 25% of a program's crews
OVERTIME_PRICE = 15                                         # $k per crew-month of overtime
CONTRACT_PRICE = {"transmission": 60, "distribution": 40, "vegetation": 25}   # $k per crew-month
POOL = 3                                                    # contractor crew-months available per year


def need_of(portfolio: Portfolio, plan: dict[str, int]) -> dict[tuple[str, int], int]:
    """Crew-months each program needs each year under a plan: m_i in every year i is worked on."""
    need = {(g, y): 0 for g in PROGRAMS for y in portfolio.years}
    for pid, t in plan.items():
        p = portfolio.project(pid)
        for y in p.spend(t):
            need[p.program, y] += p.crew_months
    return need


def year_lp(portfolio: Portfolio, year: int, need: dict[str, float], *, phase_one: bool = False):
    """The subproblem of one year. With phase_one, a shortfall variable per program measures how
    far the year is from being coverable, and the cost is the total shortfall."""
    m = mathopt.Model(name=f"crews {year}")
    rows = {}
    cost = mathopt.LinearExpression()
    for g in PROGRAMS:
        own = m.add_variable(lb=0, name=f"own_{g}")
        over = m.add_variable(lb=0, name=f"over_{g}")
        hire = m.add_variable(lb=0, name=f"hire_{g}")
        cover = own + over + hire
        if phase_one:
            short = m.add_variable(lb=0, name=f"short_{g}")
            cover += short
            cost += short
        else:
            cost += OVERTIME_PRICE * over + CONTRACT_PRICE[g] * hire
        rows[f"cover_{g}"] = m.add_linear_constraint(cover >= need[g], name=f"cover_{g}")
        rows[f"own_{g}"] = m.add_linear_constraint(own <= portfolio.crews[g, year], name=f"own_{g}")
        rows[f"over_{g}"] = m.add_linear_constraint(
            over <= OVERTIME_SHARE * portfolio.crews[g, year], name=f"over_{g}")
        rows.setdefault("hires", []).append(hire)
    rows["pool"] = m.add_linear_constraint(sum(rows.pop("hires")) <= POOL, name="pool")
    m.minimize(cost)
    return m, rows
