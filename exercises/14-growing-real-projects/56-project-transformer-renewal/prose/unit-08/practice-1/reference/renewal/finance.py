"""The plan as finance reads it: money and risk by year, against each year's budget."""

from __future__ import annotations

from dataclasses import dataclass

from .fleet import Transformer
from .report import outages, spend_by_year
from .request import Plan, Request
from .risk import risk_removed


@dataclass(frozen=True)
class YearLine:
    year: int
    units: int              # transformers replaced
    replacement: int        # $k for the units
    outages: int            # substation outages
    outage_cost: int        # $k for the outages
    total: int              # $k, replacement + outage_cost
    budget: int             # $k
    risk_removed: float     # $k over the risk window, discounted to FIRST_YEAR, base curves


def finance_lines(fleet: list[Transformer], request: Request, plan: Plan) -> list[YearLine]:
    """One line per plan year, years with no work included."""
    by_id = {t.tid: t for t in fleet}
    taken = outages(fleet, plan.replace)
    spend = spend_by_year(fleet, plan.replace, request.outage_cost)
    lines = []
    for y in request.plan_years():
        chosen = [by_id[tid] for tid, year in sorted(plan.replace.items()) if year == y]
        n_out = sum(1 for _, year in taken if year == y)
        lines.append(YearLine(
            year=y, units=len(chosen), replacement=sum(t.cost for t in chosen), outages=n_out,
            outage_cost=n_out * request.outage_cost, total=spend.get(y, 0), budget=request.budget,
            risk_removed=sum(risk_removed(t, y, request) for t in chosen)))
    return lines


def finance_report(fleet: list[Transformer], request: Request, plan: Plan) -> str:
    """A Markdown report: the table by year, the totals, and how close the plan is to the best."""
    lines = finance_lines(fleet, request, plan)
    years = request.plan_years()
    out = [f"# Transformer renewal plan, {years[0]}-{years[-1]}", "",
           f"Fleet of {len(fleet)} transformers (fictional data). All money in $k.", "",
           "| Year | Units | Replacement | Outages | Outage cost | Total | Budget | Risk removed |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for ln in lines:
        out.append(f"| {ln.year} | {ln.units} | {ln.replacement:,} | {ln.outages} | {ln.outage_cost:,} | "
                   f"{ln.total:,} | {ln.budget:,} | {ln.risk_removed:,.0f} |")
    out.append(f"| Total | {sum(ln.units for ln in lines)} | {sum(ln.replacement for ln in lines):,} | "
               f"{sum(ln.outages for ln in lines)} | {sum(ln.outage_cost for ln in lines):,} | "
               f"{sum(ln.total for ln in lines):,} | {sum(ln.budget for ln in lines):,} | "
               f"{sum(ln.risk_removed for ln in lines):,.0f} |")
    gap = (plan.bound - plan.value) / plan.bound if plan.bound else 0.0
    out += ["", f"Solver status {plan.status}. No plan under these rules removes more than "
                f"${plan.bound:,.0f}k; this one is within {gap:.2%} of that bound."]
    return "\n".join(out) + "\n"
