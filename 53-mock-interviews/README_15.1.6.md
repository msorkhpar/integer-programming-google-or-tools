# 15.1.6 Mixed Mock A: A Technical Screen

A technical screen is short and broad: one interviewer, a shared editor, many quick questions from
every area of the job, a couple of traps, and one small model to write and run. The aim is not depth
on any one topic but no gaps anywhere. Give each rapid question a two- or three-sentence answer, the
way you would on a call, then open the model answer. The interviewer's company and data are
fictional, like GridCap.

| Part | Minutes |
| --- | --- |
| Rapid round: eight questions | 8 |
| Trap questions | 4 |
| Code practice: an independent plan checker | 5 |
| Whiteboard and its code practice | 10 |

## Rapid Round: Short Answers Across Every Area

**Q1. LP, MILP or constraint programming: how do you pick?**

<details>
<summary>Model answer</summary>

An LP decides amounts and solves fast because it allows fractions; for yes/no decisions its value is
an upper bound, not a plan. A MILP adds whole-number variables and a search, and is the default for
capital planning; its answer is never better than its LP relaxation. Constraint programming searches
over logic and integers directly and suits scheduling and dense logic, with integer data. Curves keep
their guarantees only if they bend the right way; otherwise approximate them with linear pieces.

*Taught in:* lesson 1.1.3.

</details>

**Q2. The data team gives you PoF predictions. Why not just fund the riskiest assets?**

<details>
<summary>Model answer</summary>

A prediction describes the future without you; a prescription chooses what you do. Ranking by risk
ignores costs and rules: it can fund two alternatives on one asset and drop a must-do. Predictions
enter the model as coefficients and their errors travel with them, so ask how wrong a coefficient
can be before the plan changes.

*Taught in:* lesson 1.1.2.

</details>

**Q3. Linearize "value $`v`$ only if both A and B are funded".**

<details>
<summary>Model answer</summary>

Replace the product $`x_A x_B`$ with a binary $`z`$. Because $`z`$ earns a reward, the solver pushes
it up, so it needs the rows that push it down: $`z \le x_A`$ and $`z \le x_B`$. A cost on $`z`$
would need the row that pushes it up, $`z \ge x_A + x_B - 1`$. Writing all three is always correct.
HiGHS refuses the product itself.

*Taught in:* lesson 6.1.4; lesson 6.1.2.

</details>

**Q4. "At most one of these eight projects." One row or 28 pair rows?**

<details>
<summary>Model answer</summary>

One row, $`\sum_{i \in S} x_i \le 1`$. It allows the same 0/1 plans as the 28 pair rows, gives a
tighter LP bound (the pair rows let every project take a half) and is far smaller. "A implies B" is
one row too, $`x_A \le x_B`$.

*Taught in:* lesson 6.1.3; lesson 6.1.2.

</details>

**Q5. A single-budget selection is a knapsack. Is it easy?**

<details>
<summary>Model answer</summary>

With whole-number costs, dynamic programming over budget amounts solves it in $`n \times B`$ steps:
pseudo-polynomial, fast when the budget is a small number, still exponential in its number of
digits. With several budget rows (one per year) there is no single ratio to rank by, greedy rules miss
the optimum and the table needs one axis per row; that is where a MILP solver earns its place.

*Taught in:* lesson 6.3.1; lesson 3.1.3.

</details>

**Q6. What is a cover inequality?**

<details>
<summary>Model answer</summary>

A set of projects $`C`$ that cannot all fit, $`\sum_{i \in C} c_i > B`$, gives the valid row
$`\sum_{i \in C} x_i \le |C| - 1`$. It removes fractional LP points the budget row allows without
removing any plan; on GridCap tiny two cover cuts turned the LP bound 3,268.17 into the optimum 3,021
with no branching. Solvers find and add such cuts themselves.

*Taught in:* lesson 6.3.3; lesson 3.3.1.

</details>

**Q7. You added a regional spending rule and the model still solves. Done?**

<details>
<summary>Model answer</summary>

A model that solves is not yet a model that is right: a model with no such rule at all also solves,
and it allows every plan. Read the model back (domains, names, units), and let tests that fix allowed
and refused plans check each rule. Under Spec-Driven Development the rule's spec gives scenarios,
each scenario becomes a test that pairs an allowed and a refused plan, and the tests run and fail on
the old code before the code changes: in the project lesson *A regional spend share: the first
change from proposal to archive* the six tests of a regional spend share
failed on the code before the change and passed after it.

*Taught in:* lesson 12.3.1; lesson *A regional spend share: the first change from proposal to
archive*.

</details>

**Q8. Where do bad inputs get caught?**

<details>
<summary>Model answer</summary>

Before the model. A schema written from the formulation's sets and parameters validates the whole
snapshot in one pass and refuses unknown keys; a quality gate then runs every rule across projects
(parent cycles, a must-do child whose parent cannot start in time, required work that costs more
than all budgets) and reports all findings with a severity. An error blocks; a warning is reported
with the plan.

*Taught in:* lesson 12.2.1; lesson 12.2.2; lesson 9.1.2.

</details>

## Trap Questions: Quick Answers That Are Wrong

**T1. "The integrality gap is tiny here, so rounding the LP answer is good enough." Fair?**

<details>
<summary>What is wrong</summary>

A small gap means a close bound, not a safe rounding: lesson 3.1.2 shows a 1% gap beside a rounded
plan worth only 2% of the best. Rounding up or to the nearest can also break the budget (it did on
all 30 small portfolios for rounding up), and a rounded plan comes with no proof. Solve the MILP and
report its bracket.

*Taught in:* lesson 3.1.1; lesson 3.1.2.

</details>

**T2. "Look up which solver is fastest on the public benchmarks and use it." Sound?**

<details>
<summary>What is wrong</summary>

Mittelmann's public pages lost CPLEX and Xpress after 2018 and Gurobi in August 2024, so "X is
fastest" cannot be checked there. Benchmark your own models: a fixed instance set, several seeds,
time to a stated gap and the shifted geometric mean; start from the requirements as yes-or-no tests,
and weigh license cost and container fit beside speed.

*Taught in:* lesson 5.4.1; lesson 5.4.2; lesson 5.4.4.

</details>

**T3. "The run says `OPTIMAL`, so the plan follows every rule." Safe to assume?**

<details>
<summary>What is wrong</summary>

`OPTIMAL` is a claim about the model, not about the rules the business meant. A cycle of parent links
or a child that can never start still solves `OPTIMAL`, quietly dropping or bundling projects; a
loose big-M can let the integrality tolerance switch a rule off. Check the plan against the rules
with code that shares nothing with the model: it reads only the data and the plan.

*Taught in:* lesson 6.5.2; lesson 6.2.2; lesson 4.5.4; lesson 12.3.2.

</details>

The first code practice is that checker, for the whiteboard's rules, written before the model: in a
screen, it is often the first thing asked after "how would you test it?".

<!-- practice 1 -->

## Whiteboard: Projects Under a Budget, Crews and Regional Caps

"Each project has a cost, crew-weeks and a value, and belongs to a region. Choose projects for the
most value within the budget and the crew-weeks, at most so many per region. Two kinds of pairs: some
projects conflict (not both), and some need another project (A only if B). Write it and run it."

<details>
<summary>Model formulation</summary>

**Sets.** $`P`$ the projects; $`R`$ the regions, $`P_r`$ the projects in region $`r`$; $`X`$ the
conflicting pairs; $`N`$ the pairs $`(a, b)`$ where $`a`$ needs $`b`$.

**Parameters.** $`v_i`$ value; $`c_i`$ cost ($k); $`w_i`$ crew-weeks; $`B`$ the budget ($k); $`W`$
the crew-weeks available; $`k_r`$ the most projects in region $`r`$.

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)} \\
\sum_{i \in P} w_i\, x_i &\le W && && \text{(crews)} \\
\sum_{i \in P_r} x_i &\le k_r && \forall r \in R && \text{(region}_r) \\
x_a + x_b &\le 1 && \forall (a, b) \in X && \text{(conflict}_{a,b}) \\
x_a &\le x_b && \forall (a, b) \in N && \text{(needs}_{a,b})
\end{aligned}
```

Follow-ups: "Which row is the knapsack?" Budget and crews together make it multi-dimensional.
"Which one would you test first?" The needs row, whose direction is the easiest to get backwards.

</details>

<!-- practice 2 -->

## Summary

- **Rapid round.** LP for amounts, MILP for yes/no plans, CP for dense logic and scheduling;
  predictions are coefficients, not plans; a product of binaries is an AND written with rows; one
  at-most-one row beats every pair row; a knapsack's DP is pseudo-polynomial; cover rows tighten a
  budget; a model that solves is checked by tests; bad inputs are caught before the model.
- **Traps.** A small integrality gap does not make rounding safe; public benchmarks no longer
  compare the commercial solvers, so benchmark your own models; `OPTIMAL` is about the model, so an
  independent checker reads the plan against the rules.

## Reference

| Question | Lessons |
| --- | --- |
| Q1, Q2 | 1.1.3; 1.1.2 |
| Q3, Q4 | 6.1.2; 6.1.3; 6.1.4 |
| Q5, Q6 | 6.3.1; 6.3.3; 3.1.3; 3.3.1 |
| Q7 | 12.3.1; *A regional spend share: the first change from proposal to archive* |
| Q8 | 12.2.1; 12.2.2; 9.1.2 |
| T1 | 3.1.1; 3.1.2 |
| T2 | 5.4.1; 5.4.2; 5.4.4 |
| T3 | 6.5.2; 6.2.2; 4.5.4; 12.3.2 |
| Whiteboard | 6.3.1; 6.1.2; 6.1.3; project lesson *The first request: fund projects within one budget* |

**Further reading:** [MathOpt `Model` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_binary_variable`, `add_linear_constraint` and `maximize`, all the whiteboard needs); [MathOpt `result.py` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (the termination reasons a screen expects you to check before reading a plan).

## Challenges

1. Add "at least two of the North projects, or none" to the whiteboard model. Which new variable
   does it need?
2. Extend the plan checker to report by how much each budget or crew row is broken.
3. Time yourself: write the whiteboard formulation in five minutes, then compare it with the model
   answer row by row.

## Design Note: Breadth Before Depth

A screen rewards an answer that names the right tool and the right caveat in two sentences. When a
question opens a deep topic, give the short answer, then offer the detail ("I can go into the
fixed-integer re-solve if useful"). Interviewers note both the answer and the judgement about how
much to say.
