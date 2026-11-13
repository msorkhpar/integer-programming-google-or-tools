A cold-storage warehouse (not GridCap) plans each day with a handful of decisions, made for you by
`site_variables(model)`: four Booleans (`night`, `freezer`, `dock_a`, `dock_b`) and three counts
(`night_staff` from 0 to 20, `frozen_orders` from 0 to 500, `forklifts` from 0 to 6). The site
manager's rules:

```math
\begin{aligned}
\text{night} &\Rightarrow \text{night\_staff} \ge \text{min\_night} && \text{(crew)} \\
\lnot\,\text{night} &\Rightarrow \text{night\_staff} = 0 && \text{(no\_shift)} \\
\lnot\,\text{freezer} &\Rightarrow \text{frozen\_orders} = 0 && \text{(frozen)} \\
(\text{dock\_a} \land \text{dock\_b}) &\Rightarrow \text{forklifts} \ge \text{forklifts\_both} && \text{(docks)}
\end{aligned}
```

($`\land`$ is AND.) Write `add_site_rules(model, v, min_night, forklifts_both)` in `site_rules.py`,
where `v` is the dict `site_variables` returns. Each rule is one linear row switched by the right
literals; no big-M. The tests fix some decisions and ask CP-SAT whether the rules allow them. Four
lines.
