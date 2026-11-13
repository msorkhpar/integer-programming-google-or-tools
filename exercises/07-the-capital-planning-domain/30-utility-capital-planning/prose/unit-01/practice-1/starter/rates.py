from __future__ import annotations


def revenue_requirement(additions: dict[int, float], life: int, rate: float,
                        om: dict[int, float], years: list[int]) -> dict[int, float]:
    """Each year's revenue requirement: O&M + depreciation + rate x end-of-year rate base."""
    # TODO: for each year, add up O&M, the depreciation charged that year and the return on the
    # rate base at the end of the year. Every value below is a placeholder.
    return {y: 0.0 for y in years}


if __name__ == "__main__":
    print(revenue_requirement({2027: 1_000}, 4, 0.10, {}, [2027, 2028, 2029, 2030, 2031]))
