from __future__ import annotations


def constant_dollar_value(forecast: dict[int, float], nominal_rate: float, inflation: float,
                          base_year: int) -> float:
    """Value on base_year of a nominal forecast, computed in base-year dollars at the real rate."""
    real = (1 + nominal_rate) / (1 + inflation) - 1
    total = 0.0
    for year, amount in forecast.items():
        in_base_dollars = amount / (1 + inflation) ** (year - base_year)
        total += in_base_dollars / (1 + real) ** (year - base_year)
    return total


if __name__ == "__main__":
    print(constant_dollar_value({2026: -1000, 2027: 300, 2028: 300, 2029: 300, 2030: 300}, 0.08, 0.03, 2026))
