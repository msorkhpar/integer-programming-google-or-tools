"""Mock 3's traps, in numbers: three formulas that look right and are not.

1. The Weibull CDF F(a) read as next year's probability of failure (lesson 7.3.1).
2. Escalation counted from the project's start instead of the price's base year (lesson 7.2.2).
3. Benefits counted only to the end of the plan instead of the asset's life (lesson 7.2.4).
The asset and the project are made up for the question; they are not GridCap's.
"""

from __future__ import annotations

import math


def reliability(age: float, beta: float, eta: float) -> float:
    return math.exp(-((age / eta) ** beta))


def pof_views(age: float, beta: float, eta: float) -> dict[str, float]:
    r_now, r_next = reliability(age, beta, eta), reliability(age + 1, beta, eta)
    return {
        "F(a), failed by this age": 1 - r_now,
        "F(a+1) - F(a), unconditional": r_now - r_next,
        "1 - R(a+1)/R(a), next year given working": 1 - r_next / r_now,
    }


def pv(amount: float, year: int, valuation_year: int, rate: float) -> float:
    return amount / (1 + rate) ** (year - valuation_year)


def escalated_pv(cost: float, base_year: int, start: int, escalation: float, rate: float,
                 counted_from: str, valuation_year: int) -> float:
    origin = base_year if counted_from == "base year" else start
    return pv(cost * (1 + escalation) ** (start - origin), start, valuation_year, rate)


def project_npv(start: int, cost: float, benefit: float, life: int, rate: float,
                valuation_year: int, last_year: int | None) -> float:
    total = -pv(cost, start, valuation_year, rate)
    for k in range(1, life + 1):
        year = start + k
        if last_year is not None and year > last_year:
            break
        total += pv(benefit, year, valuation_year, rate)
    return total


def money(k: float) -> str:
    return f"-${-k:,.1f}k" if k < 0 else f"${k:,.1f}k"


def main() -> None:
    print("an asset aged 40, Weibull shape 3.5, scale 45 years")
    for name, value in pof_views(40, 3.5, 45).items():
        print(f"  {name:<40} {value:.3f}")
    print()
    print("$1,000k quoted in 2026 prices, escalating 4% a year, discounted at 7% to 2026")
    for start in (2027, 2030):
        cells = [f"{rule} {money(escalated_pv(1000, 2026, start, 0.04, 0.07, rule, 2026))}"
                 for rule in ("base year", "start year")]
        print(f"  start {start}: escalated from the " + ", from the ".join(cells))
    print()
    print("$900k spent in the start year, $120k of benefit a year for 25 years, 7%, valued at 2027")
    for start in (2027, 2030):
        full = project_npv(start, 900, 120, 25, 0.07, 2027, None)
        cut = project_npv(start, 900, 120, 25, 0.07, 2027, 2031)
        print(f"  start {start}: NPV over the asset's life {money(full)}, cut at the plan's end (2031) {money(cut)}")


if __name__ == "__main__":
    main()
