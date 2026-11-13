from __future__ import annotations


def years_over(spend: dict[int, float], budget: dict[int, int], rel: float = 1e-9,
               abs_tol: float = 1e-6) -> list[int]:
    """The years whose spend exceeds the budget by more than the tolerance, in increasing order."""
    # TODO: compare each year's spend with its budget plus the tolerance (see the statement).
    return [-1]


if __name__ == "__main__":
    print(years_over({2031: 500.0000000001, 2032: 640.5}, {2031: 500, 2032: 600}))
