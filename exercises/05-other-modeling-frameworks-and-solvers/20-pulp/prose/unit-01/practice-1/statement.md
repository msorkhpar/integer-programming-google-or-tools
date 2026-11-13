A water utility refurbishes some of its pump stations each year. A refurbished pump uses less
energy, so each refurbishment saves a known amount a year, but it costs money, takes crew-days, and
takes the station offline while the work is done. Some stations share a bypass main: if both of a
pair were offline at once, the district they serve would lose pressure. The regulator also names
stations that must be done this year.

In `refurbish.py`, the variables and the objective are written. Add the rows, so that:

- `build(stations, budget, crew_days, bypass_pairs)` returns the PuLP problem and its variables
  `y[sid]`, with one row per rule below, named as in the labels;
- `refurbish(...)`, already written, solves it with CBC and returns the yearly savings and the
  sorted ids of the stations to refurbish.

The formulation. $`S`$ is the stations, $`K`$ the pairs that share a bypass, $`M \subseteq S`$ the
must-do stations. Each station $`i`$ saves $`s_i`$ ($k a year), costs $`c_i`$ ($k) and takes
$`h_i`$ crew-days; the year has a budget $`B`$ and $`H`$ crew-days.

```math
\begin{aligned}
\max\ & \sum_{i \in S} s_i\, y_i && && \text{(savings)} \\
& \sum_{i \in S} c_i\, y_i \le B && && \text{(budget)} \\
& \sum_{i \in S} h_i\, y_i \le H && && \text{(crew)} \\
& y_a + y_b \le 1 && \forall (a, b) \in K && \text{(bypass}_{a,b}) \\
& y_i = 1 && \forall i \in M && \text{(must}_i) \\
& y_i \in \{0, 1\} && \forall i \in S
\end{aligned}
```

Name each row as its label says, with the ids filled in: `budget`, `crew`, `bypass_S1_S2`,
`must_S4`. A station may appear in more than one bypass pair. About six lines.

Write the model out as an LP file and read it once before you run the tests. Run and the tests
start in the course's root folder, not in this practice's folder, so `prob.writeLP("pumps.lp")`
would put `pumps.lp` at the root of the course. Write it inside your practice folder, next to
`refurbish.py`, instead: `prob.writeLP(str(Path(__file__).with_name("pumps.lp")))`, with
`from pathlib import Path` at the top.
