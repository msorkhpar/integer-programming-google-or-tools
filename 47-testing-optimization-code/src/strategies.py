"""A Hypothesis strategy for small GridCap-shaped portfolios that are feasible by construction.

The strategy draws a plan first, the *witness*, and then builds the data around it: every must-do
is a witness project, every witness child's parent is in the witness and starts early enough, no
alternative group holds two witness projects, and each year's budget is the witness's spend plus a
drawn slack. So the witness meets every rule, the model can never be infeasible on a drawn case,
and the optimum is never worse than the witness's value.
"""

from __future__ import annotations

from hypothesis import strategies as st

from gridcap import Portfolio
from tiny import YEARS, portfolio, project


class Case:
    """A drawn portfolio and a plan known to meet every rule, printed one project per item."""

    def __init__(self, portfolio: Portfolio, witness: dict[str, int]):
        self.portfolio = portfolio
        self.witness = witness

    def __repr__(self) -> str:
        rows = []
        for p in self.portfolio.projects:
            flags = [f"cost={list(p.cost_profile)}", f"window={p.earliest_start}-{p.latest_start}",
                     f"npv={p.value}"]
            if p.must_do:
                flags.append("must")
            if p.parent:
                flags.append(f"parent={p.parent} lag={p.parent_lag}")
            if p.alt_group:
                flags.append(f"alt={p.alt_group}")
            rows.append(f"{p.project_id}({', '.join(flags)})")
        budget = ", ".join(f"{y}: {b}" for y, b in self.portfolio.budget.items())
        return f"Case({'; '.join(rows)}; budget {{{budget}}}; witness {self.witness})"


@st.composite
def cases(draw, max_projects: int = 5) -> Case:
    n = draw(st.integers(min_value=1, max_value=max_projects))
    projects, witness, groups_used = [], {}, set()
    for k in range(n):
        pid = f"P{k + 1}"
        cost = tuple(draw(st.lists(st.integers(1, 50), min_size=1, max_size=2)))
        last_start = YEARS[-1] - len(cost) + 1                 # the work ends inside the horizon
        first = draw(st.integers(YEARS[0], last_start))
        last = draw(st.integers(first, last_start))
        parent, lag = None, 0
        if k > 0 and draw(st.booleans()):
            parent = draw(st.sampled_from([p.project_id for p in projects]))
            lag = draw(st.integers(0, 1))
        alt = draw(st.sampled_from([None, None, "G1", "G2"]))
        start = draw(st.integers(first, last))
        # In the witness only if the rules allow it: parent in it and early enough, group still free.
        fits = (parent is None or (parent in witness and witness[parent] + lag <= start)) \
            and alt not in groups_used
        chosen = fits and draw(st.booleans())
        must = chosen and draw(st.booleans())
        if chosen:
            witness[pid] = start
            if alt:
                groups_used.add(alt)
        projects.append(project(pid, cost, (first, last), must=must, parent=parent, lag=lag, alt=alt,
                                npv=draw(st.integers(0, 100))))
    spend = {y: 0 for y in YEARS}
    for p in projects:
        if p.project_id in witness:
            for year, amount in p.spend(witness[p.project_id]).items():
                spend[year] += amount
    budget = {y: spend[y] + draw(st.integers(0, 60)) for y in YEARS}
    return Case(portfolio(*projects, budget=budget, name="drawn"), witness)
