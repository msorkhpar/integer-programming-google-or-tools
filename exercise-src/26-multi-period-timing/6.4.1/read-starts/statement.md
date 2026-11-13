A gas utility's planners run the main-replacement model every month and hand its answer to a
reporting job. The job needs two things from each solve: every project's start year, and which
funded projects were pushed past the first year they could start. It also must not report a
schedule that is not one: last month a run stopped early and handed over values like 0.5, and the
report rounded them into a plan nobody had approved.

Write two functions in `starts.py`:

- `read_starts(values, projects, tol=1e-6)` takes the values the solver returned,
  `values[(pid, year)]`, one for each start variable, and returns every project's start year, or
  `None` for a project that is not funded. It raises `ScheduleError` when the values are not a
  schedule.
- `deferrals(starts, projects)` returns, for each funded project that starts after its earliest
  allowed year, how many years later it starts.

In the lesson's notation, the solver returns a value $`\hat x_{i,t}`$ for each $`i \in P`$ and
$`t \in T_i`$, and a solver only promises those values to within a tolerance $`\varepsilon`$ of
the domain $`\{0, 1\}`$. Before you code, write down in that notation which values are a schedule
(when is $`\hat x_{i,t}`$ read as 1, as 0, or as neither, and how many years of one project may
read as 1), and what a project's start year $`s_i`$ and its deferral are in terms of
$`\hat x_{i,t}`$ and $`\min T_i`$.

The tests hand your functions values directly, so no solver runs. About fifteen lines in total.
