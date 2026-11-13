A gas utility inherited `valves.py`, a PuLP script that picks which valves to replace this year.
It runs every night without an error, and every night it reports `Optimal`. The planners have
stopped trusting it: it once proposed more crew-weeks than the utility has, it has dropped valves
that last year's plan funded, it left the harbor district below its agreed share, and once it
returned a plan for a year when the rules could not all be met.

Fix `plan(valves, budget, crew_weeks, harbor_band, last_year)` so that it returns the plan the
formulation below defines, as `(risk cut, sorted valve ids)`, or `None` when no plan meets every
rule. The function's shape stays: same arguments, same return.

With $`V`$ the valves, $`V_H \subseteq V`$ those in the harbor district, and $`L \subseteq V`$
the valves `last_year` marks with 1. Each valve $`i`$ cuts risk by $`r_i`$ ($k a year), costs
$`c_i`$ ($k) and takes $`w_i`$ crew-weeks. The year has a budget $`B`$, $`W`$ crew-weeks, and a
harbor band from $`\ell`$ to $`u`$ ($k).

```math
\begin{aligned}
\max\ & \sum_{i \in V} r_i\, z_i && && \text{(risk\_cut)} \\
& \sum_{i \in V} c_i\, z_i \le B && && \text{(budget)} \\
& \sum_{i \in V} w_i\, z_i \le W && && \text{(crew)} \\
& \ell \le \sum_{i \in V_H} c_i\, z_i \le u && && \text{(harbor)} \\
& z_i = 1 && \forall i \in L && \text{(lock}_i) \\
& z_i \in \{0, 1\} && \forall i \in V
\end{aligned}
```

Every line of the script runs, so look for lines that do not mean what they say. The tests run
the script on small cases you could solve by hand. The reference changes five lines, counting the
import it extends with `LpStatusOptimal`. One of them becomes two rows: the reference writes the
harbor band as `harbor_min` ($`\sum_{i \in V_H} c_i z_i \ge \ell`$) and `harbor_max`
($`\sum_{i \in V_H} c_i z_i \le u`$).
