A maker of smart water meters bids for a city contract. The city's terms: at most a share
`max_share` of the meters may fail within the first `warranty_years`. The meters' lifetimes follow
a Weibull curve whose shape `beta` is fixed by the design; the characteristic life `eta` is what
the maker can still improve, with better seals and parts.

Write `required_scale(warranty_years, max_share, beta)` in `warranty.py`: the smallest `eta`
(years) that keeps the promise, so that the share failed by the end of the warranty is exactly
`max_share`.

Start from the lesson's $`F(t) = 1 - e^{-(t/\eta)^\beta}`$, set $`F(W) = q`$ for the warranty
$`W`$ and share $`q`$, and solve for $`\eta`$ on paper before you code it. The tests check your
answer with `scipy.stats.weibull_min(c=beta, scale=eta).cdf(warranty_years)`. One or two lines.
