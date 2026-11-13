"""Cover cuts on the budget knapsack: find one by hand on GridCap tiny, then run rounds on tiny and small."""

from covers import cover_rounds, is_cover, is_minimal, lp_with_cuts, separate, violation
from gridcap import generate
from selection import knapsack, solve_quiet

tiny = generate("tiny")
values = {p.project_id: p.value for p in tiny.projects}
a = {p.project_id: p.capex for p in tiny.projects}
b = tiny.capital_budget

bound, x = lp_with_cuts(values, a, b, [])
cover = ["P001", "P004", "P006", "P007"]
print(f"cover {cover}: weight {sum(a[i] for i in cover):,} > {b:,}? {is_cover(cover, a, b)}; minimal? {is_minimal(cover, a, b)}")
print(f"  at the LP point: sum of x = {sum(x[i] for i in cover):.4f}, |C| - 1 = {len(cover) - 1}, "
      f"violation {violation(cover, x):.4f}")
bigger = cover + ["P005"]
print(f"cover {bigger}: minimal? {is_minimal(bigger, a, b)}; violation {violation(bigger, x):.4f}")
print(f"greedy separation finds: {separate(a, b, x)}")


def report(name, portfolio, detail):
    sel = knapsack(portfolio)
    best = solve_quiet(sel.model).objective_value()
    values = {p.project_id: p.value for p in portfolio.projects}
    a = {p.project_id: p.capex for p in portfolio.projects}
    print(f"{name}: integer optimum {best:,.0f}")
    first = None
    for k, bound, fractional, cut in cover_rounds(values, a, portfolio.capital_budget):
        first = bound if first is None else first
        closed = (first - bound) / (first - best) if first > best else 1.0
        if detail:
            frac = ", ".join(f"{i} {v:.3f}" for i, v in fractional.items())
            added = f"add {' + '.join(cut)} <= {len(cut) - 1}" if cut else "no violated cover found"
            print(f"  round {k}: bound {bound:,.1f} (gap closed {closed:.0%}); fractional: {frac}; {added}")
        else:
            added = f"add a cover of {len(cut)} projects" if cut else "no violated cover found"
            print(f"  round {k:2}: bound {bound:,.1f} (gap closed {closed:3.0%}); "
                  f"{len(fractional)} fractional; {added}")


report("tiny", tiny, detail=True)
report("small", generate("small"), detail=False)
