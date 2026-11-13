from __future__ import annotations


def revenue_requirement(additions: dict[int, float], life: int, rate: float,
                        om: dict[int, float], years: list[int]) -> dict[int, float]:
    """Each year's revenue requirement: O&M + depreciation + rate x end-of-year rate base."""
    result = {}
    for y in years:
        depreciation = 0.0
        rate_base = 0.0
        for placed, cost in additions.items():
            age = y - placed + 1                  # years in service at the end of year y
            if age < 1:
                continue
            annual = cost / life
            if age <= life:
                depreciation += annual
            rate_base += max(0.0, cost - annual * min(age, life))
        result[y] = om.get(y, 0.0) + depreciation + rate * rate_base
    return result


if __name__ == "__main__":
    print(revenue_requirement({2027: 1_000}, 4, 0.10, {}, [2027, 2028, 2029, 2030, 2031]))
