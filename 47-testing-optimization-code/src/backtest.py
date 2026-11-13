"""Back-test today's model against GridCap's (invented) past planning cycles.

For each past cycle: solve that cycle's snapshot with today's model, then set the result beside the
plan the cycle approved. Every difference is a question to put to a planner, not an error.
GridCap and its history are fictional (see history.py).
"""

from __future__ import annotations

from audit import spend_by_year, value, violations
from history import CYCLES, approved, snapshot
from plan_model import optimize


def diff(was: dict[str, int], now: dict[str, int]) -> dict[str, list[str]]:
    """Projects kept in the same year, moved, added and dropped between two plans."""
    return {"kept": [p for p in was if now.get(p) == was[p]],
            "moved": [p for p in was if p in now and now[p] != was[p]],
            "added": [p for p in now if p not in was],
            "dropped": [p for p in was if p not in now]}


def backtest(cycle: int) -> dict:
    portfolio = snapshot(cycle)
    then = approved(cycle)
    status, npv, now = optimize(portfolio)
    return {"cycle": cycle, "status": status, "then": then, "now": now, "diff": diff(then, now),
            "then_npv": value(portfolio, then), "now_npv": value(portfolio, now),
            "then_breaks": violations(portfolio, then), "now_breaks": violations(portfolio, now),
            "then_spend": spend_by_year(portfolio, then), "budget": dict(portfolio.budget)}


def main() -> None:
    for cycle in CYCLES:
        r = backtest(cycle)
        d = r["diff"]
        print(f"cycle {cycle}: today's model {r['status']}, NPV {r['now_npv']:,} against approved {r['then_npv']:,} "
              f"({r['now_npv'] - r['then_npv']:+,})")
        print(f"  {len(d['kept'])} kept, {len(d['moved'])} moved, {len(d['added'])} added, "
              f"{len(d['dropped'])} dropped; today's plan breaks {len(r['now_breaks'])} rules")
        print(f"  the approved plan breaks {len(r['then_breaks'])} of today's rules"
              + (f", first: {r['then_breaks'][0]}" if r["then_breaks"] else ""))


if __name__ == "__main__":
    main()
