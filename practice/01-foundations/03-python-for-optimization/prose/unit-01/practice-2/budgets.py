from __future__ import annotations

import pandas as pd


def budget_problems(budgets: pd.DataFrame, years: list[int], regions: list[str]) -> list[str]:
    """One string per problem in a budgets table (see the statement's table)."""
    # TODO: one boolean mask per rule, then the pairs that have no row at all.
    return ["not checked yet"]


if __name__ == "__main__":
    import io
    demo = pd.read_csv(io.StringIO("year,region,budget\n2031,North,500\n2031,North,-5\n"))
    print(budget_problems(demo, [2031], ["North", "South"]))
