"""Swing weighting: rate each measure's swing against the biggest one, then divide by the total."""

from value_function import MEASURES, REFERENCE, SWING_RATINGS, exchange_rates, swing_weights

print("the swings the board compared (from no benefit to the reference):")
for k, (_, unit) in MEASURES.items():
    print(f"  {k:13} 0 -> {REFERENCE[k]:>9,} {unit}")
weights = swing_weights(SWING_RATINGS)
print("ratings:", SWING_RATINGS)
print("weights:", {k: round(w, 4) for k, w in weights.items()}, "sum", round(sum(weights.values()), 6))
rates = exchange_rates(REFERENCE, weights)
print("what the weights say, in NPV:")
print(f"  avoiding 1 customer-minute is worth ${rates['reliability'] * 1000:,.2f}")
print(f"  avoiding 1 safety incident is worth ${rates['safety']:,.0f}k")
print(f"  avoiding 1 tonne CO2e is worth ${rates['environmental']:,.2f}k")
