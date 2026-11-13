from __future__ import annotations


def npv_by_start_year(costs: tuple[float, ...], annual_benefit: float, life: int, starts,
                      valuation_year: int, rate: float, escalation: float) -> dict[int, float]:
    """{start year: NPV on the start of valuation_year} for a relining job."""
    table = {}
    for start in starts:
        cash = {}
        for k, cost in enumerate(costs):
            cash[start + k] = cash.get(start + k, 0.0) - cost
        first_benefit = start + len(costs)
        for year in range(first_benefit, first_benefit + life):
            cash[year] = cash.get(year, 0.0) + annual_benefit
        value = 0.0
        for year, amount in cash.items():
            nominal = amount * (1 + escalation) ** (year - valuation_year)
            value += nominal / (1 + rate) ** (year - valuation_year)
        table[start] = value
    return table


if __name__ == "__main__":
    print(npv_by_start_year((400, 400), 90, 20, (2027, 2028, 2029), 2027, 0.06, 0.02))
