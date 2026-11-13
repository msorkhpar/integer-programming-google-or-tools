from __future__ import annotations


def npv_by_start_year(costs: tuple[float, ...], annual_benefit: float, life: int, starts,
                      valuation_year: int, rate: float, escalation: float) -> dict[int, float]:
    """{start year: NPV on the start of valuation_year} for a relining job."""
    # TODO: build each start's cash flow by calendar year, escalate it, and discount it to valuation_year.
    return {t: 0.0 for t in starts}


if __name__ == "__main__":
    print(npv_by_start_year((400, 400), 90, 20, (2027, 2028, 2029), 2027, 0.06, 0.02))
