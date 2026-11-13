A rail depot chooses which overhaul jobs to do this week. Each job takes hours and is worth an
amount if done. Hours beyond the regular week are overtime, bought from a contractor whose price
per hour changes by tier: some contracts get dearer with volume, and some give a volume discount.
The depot wants the jobs that maximize value minus what the overtime costs.

Write `plan(jobs, regular, hours, cost)` in `overtime.py`. `jobs` maps a job to `(hours, value)`;
the overtime cost is the piecewise-linear curve through the points `(hours[k], cost[k])`. Return
the net value, the overtime hours and their cost.

```math
\begin{aligned}
\max \;& \sum_{j \in J} \text{value}_j\, x_j - p \\
& \sum_{j \in J} \text{hours}_j\, x_j \le R + o && \text{(time)} \\
& p \ge f(o) && \text{(curve)} \\
& x_j \in \{0, 1\}, \quad \text{hours}_0 \le o \le \text{hours}_{K}, \quad p \ge 0
\end{aligned}
```

Write the curve row with `pyomo.environ.Piecewise`. The tests use both kinds of contract and solve
with `appsi_highs`, so choose the arguments so that every curve is exact and HiGHS accepts the
model. About fifteen lines.
