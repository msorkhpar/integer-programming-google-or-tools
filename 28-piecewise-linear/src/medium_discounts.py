"""Lesson 6.6.3: three volume-discount curves on GridCap medium, with each form, by size and search.

GridCap is a fictional utility's portfolio, and the discounts are invented for this lesson. Each
program's contractor invoices its total list-price work W on a falling-rate curve: K tiers of equal
width across the program's whole list price, the rate per $k falling evenly from 1.00 to 0.60. The
three invoices together must fit the capital budget. HiGHS solves each form to a zero gap; the
program prints its branch-and-bound node count.
"""

from gridcap import generate
from piecewise import FORMS, Curve
from selection import EXACT, build, ids, solve_highs

PROGRAMS = ("transmission", "distribution", "vegetation")
SHARE = 0.8                                      # the invoices must fit 80% of the capital budget


def discount_curve(total: float, K: int, first: float = 1.0, last: float = 0.6) -> Curve:
    xs = [total * k / K for k in range(K + 1)]
    ys = [0.0]
    for k in range(K):
        rate = first - (first - last) * k / (K - 1)
        ys.append(ys[-1] + rate * (xs[k + 1] - xs[k]))
    return Curve(tuple(xs), tuple(ys))


def with_discounts(portfolio, K, form, *, integer=True):
    sel = build(portfolio, integer=integer)
    model = sel.model
    model.delete_linear_constraint(sel.budget)
    invoices, binaries = 0, 0
    for program in PROGRAMS:
        members = ids(portfolio, program=program)
        work = sum(portfolio.project(i).capex * sel.x[i] for i in members)
        piece = form(model, discount_curve(sum(portfolio.project(i).capex for i in members), K), program)
        model.add_linear_constraint(piece.x == work, name=f"work_{program}")
        invoices += piece.y
        binaries += len(piece.binaries)
        for v in piece.binaries:
            v.integer = integer
    model.add_linear_constraint(invoices <= SHARE * portfolio.capital_budget, name="budget")
    return sel, binaries


if __name__ == "__main__":
    medium = generate("medium")
    print(f"GridCap medium, {len(medium.projects)} projects, invoices within ${SHARE * medium.capital_budget:,.0f}k")
    print(" K | form        | curve binaries | rows | MILP       | LP bound     | nodes")
    for K in (4, 8, 16):
        for name, form in FORMS.items():
            sel, binaries = with_discounts(medium, K, form)
            result = solve_highs(sel.model, EXACT)
            lp = solve_highs(with_discounts(medium, K, form, integer=False)[0].model)
            print(f"{K:2} | {name:11} | {binaries:14} | {sel.model.get_num_linear_constraints():4} | "
                  f"${result.objective_value():,.0f}k | ${lp.objective_value():,.1f}k | {result.solve_stats.node_count:5,}")
