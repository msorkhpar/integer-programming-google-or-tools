A retailer's promotion model (not GridCap) has an integer `spend`, a customer's spend in whole dollars,
and a Boolean `gold`. Several parts of the model read `gold`: some reward it, some charge for it, and
a report prints it. So `gold` must be true exactly when the spend reaches the threshold:

```math
\text{gold} \iff \text{spend} \ge \text{threshold} \qquad \text{(tier)}
```

($`\iff`$ is "if and only if": each side implies the other.) Write
`add_tier_flag(model, spend, gold, threshold)` in `tier.py` with `only_enforce_if`. Spend is a whole
number, so "below the threshold" is a row with a whole-number bound too. The tests fix the spend and
the flag and ask CP-SAT whether your rows allow the pair. Two lines.
