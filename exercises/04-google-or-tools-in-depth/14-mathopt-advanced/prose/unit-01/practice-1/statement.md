A small island grid schedules its diesel units for the next hour. Each unit in `units` has a name,
a minimum output `min_mw` and a maximum `max_mw`. A unit is either off, and then it makes no power
at all, or on, and then it must run at least at its minimum: a diesel engine cannot idle at 3 MW
when its minimum stable load is 10 MW.

The model in `units.py` already has, for every unit $`u`$, a binary $`\text{on}_u`$ and a continuous
output $`0 \le p_u \le \text{max}_u`$, and a row making the units meet the hour's demand. Write
`add_unit_rules(model, on, power, units)` so that the model states the two rules, each as one
MathOpt indicator constraint per unit:

```math
\begin{aligned}
\text{on}_u = 0 \;&\Longrightarrow\; p_u \le 0 && \forall u && \text{(off}_u) \\
\text{on}_u = 1 \;&\Longrightarrow\; p_u \ge \text{min}_u && \forall u && \text{(on}_u)
\end{aligned}
```

With $`p_u \ge 0`$ as a bound, $`p_u \le 0`$ means $`p_u = 0`$, and the bound $`p_u \le \text{max}_u`$
already caps a running unit. Each implied row has one side, which is what SCIP accepts (lesson 4.3.1).

`on` and `power` are dicts keyed by unit name. Name the constraints `off_<name>` and `on_<name>`.

The tests fix each unit's on/off state and output, and ask SCIP whether the model accepts that hour,
so any correct way of writing the two rules passes. HiGHS would refuse the model: lesson 4.3.1 shows
which solvers take indicator constraints. About six lines.
