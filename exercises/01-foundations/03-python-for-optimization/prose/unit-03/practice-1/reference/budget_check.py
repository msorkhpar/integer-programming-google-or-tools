from __future__ import annotations


def years_over(spend: dict[int, float], budget: dict[int, int], rel: float = 1e-9,
               abs_tol: float = 1e-6) -> list[int]:
    """The years whose spend exceeds the budget by more than the tolerance, in increasing order."""
    over = []
    for year in sorted(spend):
        allowed = budget[year] + max(rel * abs(budget[year]), abs_tol)
        if spend[year] > allowed:
            over.append(year)
    return over


if __name__ == "__main__":
    print(years_over({2031: 500.0000000001, 2032: 640.5}, {2031: 500, 2032: 600}))
