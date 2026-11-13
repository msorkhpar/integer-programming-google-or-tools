"""Conditional and unconditional next-year PoF for one asset's curve, as it ages."""

from asset_risk import cumulative_pof, next_year_pof, tiny

a = tiny.asset("A006")
print(f"A006: beta {a.weibull_beta}, eta {a.weibull_eta} years")
for age in (10, 30, 50, 70, 90):
    unconditional = cumulative_pof(age + 1, a.weibull_beta, a.weibull_eta) - cumulative_pof(age, a.weibull_beta, a.weibull_eta)
    print(f"age {age:>2}: unconditional {unconditional:.4f}  conditional {next_year_pof(age, a.weibull_beta, a.weibull_eta):.4f}")
