"""A weight is an exchange rate between units: w_k / R_k is what one unit of measure k is worth."""

from value_function import REFERENCE, exchange_rates

importance = {"safety": 0.4, "reliability": 0.3, "financial": 0.2, "environmental": 0.1}


def show(label, reference, weights):
    rates = exchange_rates(reference, weights)
    print(f"{label}:")
    print(f"  1 customer-minute = ${rates['reliability'] * 1000:,.2f}")
    print(f"  1 safety incident = ${rates['safety']:,.0f}k")
    print(f"  1 tonne CO2e      = ${rates['environmental']:,.2f}k")


show("importance weights, safety swing 1 incident", REFERENCE, importance)
show("importance weights, safety swing 0.1 incident", {**REFERENCE, "safety": 0.1}, importance)
