The planning team's model passed its unit tests and its golden record. Before it goes into service,
the team wants evidence that its rules hold on portfolios nobody wrote by hand. Your milestone draws
practice portfolios (invented test data for a fictional utility) with Hypothesis and checks
properties of every plan the model returns.

`drawn_properties.py` gives you milestone 2's model with a reduced rule set (must-do, at-most-once,
alternative, precedence-with-lag and yearly budget rows), `solve`, `plan_of`, `value` and the rule
checker `check(snapshot, plan)`, which reads only the data. `build(snapshot, skip)` can plant a bug
for testing your tests: `skip` may hold `"must"`, `"alt"`, `"budget"` (those rows left out), `"lag"`
(every lag read as 0) or `"value"` (a stray 1 added to the objective). A drawn portfolio uses the
years 2027 to 2029 and the milestones' project fields: `cost`, `earliest`, `latest`, `must`,
`parent`, `lag`, `group`, `npv`.

Write:

| function | contract | lesson |
| --- | --- | --- |
| `portfolios()` | a Hypothesis strategy (`st.composite`) that returns `(snapshot, witness)`: one to six projects, and a witness plan that breaks no rule. Draw the witness while you draw the projects (a project can join it only when its parent is in it early enough, lag included, and its group is still free; only a project the witness funds can be a must-do), then set each year's budget to the witness's spend there plus a tight slack ($0k to $40k, in steps of $10k) or a loose one ($1,000k). Draw parents, lags of 0 or 1, groups and must-dos, and an NPV that falls $5k per year of delay | 12.3.2 |
| `holds(snapshot, witness, skip)` | solve `build(snapshot, skip)` and fail an `assert` unless: the status is OPTIMAL; the plan breaks no rule (`check`); the reported objective equals the plan's value; the plan is worth at least the witness; and $10k more in every year never lowers the optimum | 12.3.2, 12.3.3 |

The reference draws its portfolios this way; other choices pass as long as every planted bug is
still caught:

- **Costs and windows.** A cost profile of one or two years, each amount a multiple of $10k from
  $10k to $90k. The window lies inside 2027 to 2029 and leaves room for the whole profile: the
  latest start is at most 2029 minus the profile's length plus one.
- **Links.** A parent is drawn from the projects already drawn, or none; the lag is 0 or 1 when
  there is a parent; the group is none (two chances in three) or `"G1"`.
- **The witness.** One start year is drawn in the window. The project may join the witness only if
  its parent is in it and started at least the lag earlier, and no project of its group is in it;
  if it may, a coin decides.
- **Must-dos.** Only a project the witness funds can be a must-do, and a second coin decides
  whether it is one. A project outside the witness is never a must-do, so the witness keeps every
  must-do row.
- **NPV.** A base value from −$10k to $100k at the earliest start, $5k less for each year the
  start is later.

The tests run your strategy on 200 portfolios (`max_examples=200`, `derandomize=True`, no database,
no deadline), expect every property to hold for the correct model, and expect each planted bug to be
caught by some drawn portfolio. A bug that no drawn case can show is a hole in the strategy, not in
the model. About forty lines.
