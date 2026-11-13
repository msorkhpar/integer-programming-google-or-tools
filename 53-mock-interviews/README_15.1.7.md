# 15.1.7 Mixed Mock B: An Onsite Loop

The last mock is a full day compressed into one page: a modeling round with the hiring manager, a
coding round, a system design round, a round on explaining results to people who are not modelers,
and a deep dive into something you built. Each interviewer writes a separate verdict, so each round
must stand on its own. The company is fictional, like GridCap, and the projects you will talk about
in the deep dive are the course's own capstone and grown projects.

| Part | Minutes |
| --- | --- |
| System design, explaining and deep-dive rounds: six questions | 11 |
| Trap questions | 4 |
| Coding round: what a decision costs | 7 |
| Modeling round: the whiteboard and its code | 10 |

## System Design: Scenarios Are Data, and Every Run Is Reproducible

**Q1. Design the scenario workflow: planners create, copy and optimize scenarios through the
planning cycle.**

<details>
<summary>Model answer</summary>

A scenario is a record of inputs (data, budgets, overrides, settings) kept apart from the model, with
metadata (id, name, who, when, parent) that never enters the model. Its snapshot is a hash of the
inputs only, so equal inputs give equal ids, and a result is current only while its snapshot equals
its scenario's. A copy shares nothing mutable with its parent. The cycle's states (Initial, Pre-Opt,
Post-Opt, Budget Lock) live in one transition table that every request is checked against; a write
names the version it read, and a stale write is refused (optimistic locking, the version check in
the UPDATE's WHERE clause). Budget Lock needs a current optimal run, and a cycle has one plan of
record. Overrides are requests checked against the data and appended to an audit trail. In the
course all of this is stored in SQLite, with the database itself refusing what no caller may do
(triggers freeze locked scenarios, a partial unique index allows one plan of record per cycle).
Lesson 12.1.3 built the optimistic locking; lesson 12.1.4 built the triggers and the partial unique
index.

*Taught in:* lesson 7.1.3; lesson 12.1.1; lesson 12.1.2; lesson 12.1.3; lesson 12.1.4.

</details>

**Q2. Follow one run from the planner's click to the result on screen.**

<details>
<summary>Model answer</summary>

The API validates the request against its schema (422 for a bad body), writes the snapshot to S3
under its digest, and answers 202 with a run id. A Step Functions execution, named after the run so a
retry cannot start it twice, submits an AWS Batch job on Fargate that runs the solver container from
the same image as the API; the job reads the snapshot, re-hashes it, solves with pinned settings and
writes the result under the snapshot's key, conditionally, so nothing is overwritten. A failed job is
caught and a `failed` result written once. The planner's screen polls the run's status and fetches a
result with the plan, money by year, value, gap, status and a message; an infeasible scenario comes
back as a result, not an error.

*Taught in:* lesson 12.4.2; lesson 12.4.3; lesson 12.5.2; lesson 12.5.3; mock 5 (*Mock 5:
production, trust and performance*) for the trust questions that follow.

</details>

**Q3. The cloud team offers GPU instances for the solver jobs. What changes in the design?**

<details>
<summary>Model answer</summary>

Less than they expect, and the GPU stays optional. The CPU path remains the default, and a GPU job
falls back to it with the same answer within tolerance. The job detects a GPU when it starts rather
than assuming one: in the CUDA build of HiGHS, PDLP with no GPU killed the process instead of
returning an error (lesson 11.4.2 showed it), and a container engine without the NVIDIA runtime
passes no GPU through. So
the design checks whether the compute environment that runs the solve offers GPUs at all, and if it
doesn't, adds GPU instances as a second queue beside the CPU one. The default image stays free of CUDA; a separate, optional GPU image
carries HiGHS's CUDA build and cuOpt. What goes there is large LPs, with the method fixed to PDLP so
that a rerun repeats; a MILP's branch-and-bound stays on the CPU either way. The run's manifest
records the device, the method and the tolerance, and a plan from a GPU MILP solve is checked for
feasibility and objective on the CPU before it can reach Budget Lock.

*Follow-ups.* "Is it worth the instances?" Measure at your own sizes: on a 1M-variable
transportation LP the GPU cut 10.3 s on the CPU to under 2 s, while a small LP gains nothing and the
first solve pays about 0.2 s of CUDA start-up. "Two GPU runs disagreed; what now?" That is round 3
of lesson *Mock 5: production, trust and performance*.

*Taught in:* lesson 11.4.2; lesson 11.4.3; lesson 11.4.4; lesson 11.4.6; lesson 12.5.2.

</details>

## Explaining: Numbers With Their Units, Direction and Conditions

**Q4. In an LP for crew planning, the dual value of the contractor-hours row is 0.07 in $k per hour.
Explain it to a finance partner.**

<details>
<summary>Model answer</summary>

Say its unit, its direction and its range, in the partner's units: one more contractor hour is worth
$70 of value, for small changes, until another row starts to bind; the solver's ranging gives that
range. Inside the range, price times amount is exact; beyond it, in a maximization, the price
overstates the gain, so a large change needs a re-solve. A negative price is the marginal cost of a
commitment. And if the model were a MILP, there would be no price to explain: tell finance the
steps of the budget-value curve instead (mock 4).

*Taught in:* lesson 2.3.3; lesson 2.3.4; lesson 9.2.4.

</details>

**Q5. One run, three readers: planners, finance and auditors. What does each get?**

<details>
<summary>Model answer</summary>

Write one record per run (inputs, snapshot, status, bound, plan, diff, priced reasons, spend, checks)
and generate every text from it. Planners read projects: in, when, out, the rule behind each in words,
the price of undoing it, and the close calls. Finance reads money by year against budget and against
the previous plan, the change in value, and whether it is proven (NPV with its gap). Auditors read
inputs, software and settings, and rule checks computed from the data that they can repeat without
the model; a rerun is stated as evidence.

*Taught in:* lesson 9.3.4; lesson 7.1.4.

</details>

## Deep Dive: Walk Through Something You Built

**Q6. "Tell me about an optimization system you built, end to end."**

<details>
<summary>Model answer</summary>

Use the course's capstone, CIPT Lite, and say it is a course project on a fictional utility's data.
Structure it by its milestones: a snapshot loaded, validated and named by its content hash (lesson
*Data: load, validate and snapshot the portfolio*); the multi-period model with every section
6 rule and an independent rule checker (*Model: multi-period selection with all section 6
rules*); value coefficients (*Value: NPV by start year, risk reduction from PoF/RUL, weighted
value*); diagnostics (*Diagnostics: pre-solve checks, IIS message, why-deferred report*);
trust (*Trust: determinism harness, Hypothesis properties, golden test, warm start*); and the
service (*Service: FastAPI job API, moto-tested S3 store, Pareto frontier endpoint*). For each,
say one decision you made and its trade-off. If asked how a model grows with its requirements, the
grown projects follow one model through many requests: the vegetation crew planner project, from
its first request to its service; the CIPT planner project, from a one-budget selection to its trust
harness; and the transformer fleet renewal project, from a worst-first list to its handoff to
finance.

*Follow-ups.* "What would you do differently?" Name a measured limit, not a feeling. "What broke?"
A test that failed for the right reason, and what it caught.

</details>

## Trap Questions: Answers That Fail a Design Review

**T1. "Lambda is serverless and scales, so run the solve in a Lambda function." Good design?**

<details>
<summary>What is wrong</summary>

A Lambda invocation runs for at most 900 seconds, and a capital plan can take longer; Lambda does
short glue (writing a `failed` result, routing). The solve runs neither in Lambda nor in the API
process, which only answers requests: it runs as an AWS Batch job on Fargate, whose timeout is set
above the solver's own limit, and Step Functions waits for it.

*Taught in:* lesson 12.5.2.

</details>

**T2. "If the scenario is infeasible, the API returns HTTP 500." Right?**

<details>
<summary>What is wrong</summary>

An infeasible scenario is an answer: 200 with `status: infeasible` and the planner message. 4xx is
for a bad request (FastAPI's 422 for a body that breaks the schema), 5xx only for a broken server.
And `infeasible` is reported only when proven; a limit with no plan is its own status.

*Taught in:* lesson 12.4.1; lesson 12.4.2.

</details>

**T3. "Money not spent is carried over, so write the cash row as an equation: spend plus carry-out
equals budget plus carry-in." Correct?**

<details>
<summary>What is wrong</summary>

Money that is neither spent nor carried lapses, so the cash row is an inequality,
$`\text{spend}_y + r_y \le B_y + r_{y-1}`$. Written as an equation, it forces every unspent dollar
into the carry, and with a cap on the carry a plan that spends less than it could becomes infeasible:
a feasible plan turns into an infeasible model.

*Taught in:* lesson 6.4.4.

</details>

**T4. "CapEx, OpEx and the resilience fund add up to the yearly budget, so one pooled row per year
is enough." Is it?**

<details>
<summary>What is wrong</summary>

One pooled budget allows plans the pots refuse: a plan can spend the fund's money on CapEx work. Each
pot gets its own row per year. To find which pot's row costs the most, drop it and solve again: in an
integer program a row with slack can still keep out a whole project.

*Taught in:* lesson 6.4.4.

</details>

**T5. "Override A costs $300k and override B $200k, so together they cost $500k." Safe to add?**

<details>
<summary>What is wrong</summary>

Costs of decisions do not add up: in lesson 6.5.6 four overrides cost $618k one at a time and $927k
together, and the costs of mandates do not add either (lesson 6.5.1). The four together cost more
than the sum of their single costs, so more than any one of them: no rule of thumb (the sum, the
largest single cost, or a discount for overlap) stands in for the joint cost. Price the set by
solving with all of them, and change one input at a time when you need to charge a difference to its cause.

*Taught in:* lesson 6.5.6; lesson 6.5.1; lesson 9.3.3.

</details>

## Coding Round: What a Decision Costs

"Write a function that, for each project, says what the best plan loses if that decision is
reversed: funded projects forced out, unfunded ones forced in. Use the solver; we will compare with
brute force." This is Q5 of mock 4 as code: one model built once, a bound changed and restored per
project, and a forcing the rules cannot satisfy answered with no number.

<!-- practice 1 -->

## Modeling Round: Carry-Over Cash and a Regional Floor

The hiring manager: "Our budgets carry over: what a year does not spend may be spent later, but at
most half of a year's budget can be carried out of it. Projects spend over several years. Each
region must see at least a minimum spend over the plan. Write the model, then code it."

<details>
<summary>Model formulation</summary>

**Sets.** $`P`$ the projects; $`Y = (y_0, \dots, y_n)`$ the plan's years in order; $`T_i \subseteq
Y`$ the start years of project $`i`$; $`R`$ the regions, $`P_r`$ the projects in region $`r`$.

**Parameters.** $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k);
$`B_y`$, the budget of year $`y`$ ($k); $`\alpha`$, the share of a year's budget that may be
carried out of it; $`F_r`$, region $`r`$'s minimum spend over the plan's years ($k); $`v_{i,t}`$,
the value of starting $`i`$ in year $`t`$.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$; $`r_y \ge 0`$, the money
carried out of year $`y`$ ($k), with $`r_{y_0 - 1} = 0`$. Write
$`\text{spend}_y(S) = \sum_{i \in S} \sum_{t \in T_i,\ 0 \le y - t < |c_i|} c_{i,y-t}\, x_{i,t}`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P && \text{(once}_i) \\
\text{spend}_y(P) + r_y &\le B_y + r_{y-1} && \forall y \in Y && \text{(cash}_y) \\
r_y &\le \alpha\, B_y && \forall y \in Y && \text{(carry\_cap}_y) \\
\sum_{y \in Y} \text{spend}_y(P_r) &\ge F_r && \forall r \in R && \text{(floor}_r)
\end{aligned}
```

The floor counts spend inside the plan's years only. Follow-ups: "Can the floors make it
infeasible?" Yes; check each floor against the most its region can spend, and all floors against all
budgets, knowing that passing both checks does not prove a plan exists (lesson 6.5.5). "What does a
floor cost?" Solve with and without it; spending every dollar cost $5,228k of NPV on GridCap.

</details>

<!-- practice 2 -->

## Summary

- **System design.** A scenario is a record of inputs named by its snapshot; states live in one
  transition table; stale writes are refused; one plan of record per cycle; the run goes API, S3,
  Step Functions, Batch on Fargate, S3, poll and fetch. A GPU is an optional queue for large LPs,
  with a CPU fallback, the device in the manifest and GPU MILP plans checked on the CPU.
- **Explaining.** A price with its unit, direction and range; for a MILP, the steps. One record per
  run, a text per reader.
- **Deep dive.** The capstone's six milestones, each with one decision and its trade-off.
- **Traps.** Lambda is glue, never the solve (900 s at most). Infeasible is an answer, not a 500. The
  cash row is an inequality, because money lapses. Pots need their own rows. Costs of overrides do
  not add up.

## Reference

| Question | Lessons |
| --- | --- |
| Q1 scenario workflow | 7.1.3; 12.1.1; 12.1.2; 12.1.3; 12.1.4 |
| Q2, T1, T2 one run | 12.4.1; 12.4.2; 12.4.3; 12.5.2; 12.5.3 |
| Q3 GPU jobs | 11.4.2; 11.4.3; 11.4.4; 11.4.6; 12.5.2 |
| Q4, Q5 explaining | 2.3.3; 2.3.4; 9.2.4; 9.3.4; 7.1.4 |
| Q6 deep dive | the capstone, CIPT Lite (all six lessons); the grown projects: the vegetation crew planner, the CIPT planner and the transformer fleet renewal (every lesson of each) |
| T3, T4 cash and pots | 6.4.4 |
| T5, coding round | 6.5.6; 6.5.1; 9.3.2; 9.3.3; 4.3.4 |
| Modeling round | 6.4.2; 6.4.4; 6.5.5 |

**Further reading:** [MathOpt `Model` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_variable` with its bounds, the carry variables of the modeling round); [MathOpt `variables.py` (OR-Tools source, read in the pinned 9.15 wheel)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/variables.py) (`lower_bound` and `upper_bound` as settable properties, which the coding round changes and restores).

## Challenges

1. Add a cap on the total carried over the whole plan to the modeling round. Which variables does it
   sum?
2. In the coding round, report for each reversal which projects gave way, not only the cost.
3. Draw the system design of Q2 on one page, with each arrow labelled by what it carries.

## Design Note: Each Round Is Its Own Verdict

An onsite loop is several interviews, each with its own written verdict, read together afterwards.
A strong modeling round does not cover a weak design round. Practise each round on its own clock,
and end each answer with the condition or trade-off that the next question would ask about.
