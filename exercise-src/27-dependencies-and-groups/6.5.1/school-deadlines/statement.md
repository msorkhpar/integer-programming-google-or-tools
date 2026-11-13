A school district plans its building work for 2027 to 2030. The model in `schools.py` has a
binary `x[pid, t]` for each project and each year `t` in its `starts` (1 if the project starts in
year `t`). Three rules come from the state and the district's own policy:

- **Once.** No project starts more than once.
- **Required work.** `required` maps a project to a deadline year. A required project must be done,
  and it must start in its deadline year or earlier.
- **Accessibility.** `access` maps a school to its accessibility projects (ramps, lifts, doors),
  and `targets` maps a school to a pair `(k, year)`: by the end of `year`, at least `k` of that
  school's accessibility projects must have started. Which ones is up to the plan.

Write `add_mandates(model, x, projects, required, access, targets)` so that the model allows
exactly the plans that keep all three rules.

The model so far, with $`P`$ the projects and $`T_i`$ the start years of project $`i`$:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the remaining sets and parameters (the required projects and their deadlines, the schools,
each school's access projects, its count and its year), then write your rows, each with its
quantifier and a label, and only then code them. Before you write the access row, ask which of a
project's start variables should count toward a target year.

The tests fix every `x[pid, t]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About ten lines.
