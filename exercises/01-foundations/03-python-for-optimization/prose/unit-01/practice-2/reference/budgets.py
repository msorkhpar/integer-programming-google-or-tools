from __future__ import annotations

import pandas as pd


def budget_problems(budgets: pd.DataFrame, years: list[int], regions: list[str]) -> list[str]:
    """One string per problem in a budgets table (see the statement's table)."""
    amount = pd.to_numeric(budgets["budget"], errors="coerce")
    rules = {
        "budget is not a number": amount.isna(),
        "negative budget": amount < 0,
        "unknown region": ~budgets["region"].isin(regions),
        "year outside the plan": ~budgets["year"].isin(years),
        "duplicate": budgets.duplicated(["year", "region"], keep=False),
    }
    problems = []
    for reason, mask in rules.items():
        problems += [f"line {n}: {reason}" for n in budgets.index[mask] + 2]
    present = set(zip(budgets["year"], budgets["region"]))
    problems += [f"missing {y} {r}" for y in years for r in regions if (y, r) not in present]
    return problems


if __name__ == "__main__":
    import io
    demo = pd.read_csv(io.StringIO("year,region,budget\n2031,North,500\n2031,North,-5\n"))
    print(budget_problems(demo, [2031], ["North", "South"]))
