The feeder team exports its candidate projects as two CSV files, and the selection model needs
three of its parameters from them. For each project $`i \in P`$:

```math
\begin{aligned}
\text{capex}_i &= \sum_{k} c_{i,k} && \text{(the sum of the yearly costs } c_{i,k} \text{ in its cost profile)} \\
\text{value}_i &= \text{npv}_{i,\,e_i} && \text{(its NPV if it starts in its earliest start year } e_i\text{)}
\end{aligned}
```

and, for each child project $`c \in C`$, its parent $`p(c)`$. A project whose parent cell is blank is
not a child.

Write `model_inputs(projects, npv)` in `inputs.py`. It returns three dicts keyed by project id:
`capex`, `value`, and `parent` (child id to parent id, children only).

- `projects` has the columns `project_id`, `cost_profile` (yearly costs joined by `;`, for example
  `300;200`), `earliest_start` and `parent`.
- `npv` is long: the columns `project_id`, `start_year` and `npv`, one row per project and start year.

Both frames come straight from `pd.read_csv` with no `dtype=`, as the team's loader reads them, so
every column has the type pandas guessed for that file.

About six lines.
