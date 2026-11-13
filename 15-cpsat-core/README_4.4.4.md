# 4.4.4 When CP-SAT Beats MIP, and When It Doesn't

GridCap now has two solvers that can take its selection model: HiGHS through MathOpt, which proves
optimality with LP bounds (lesson 3.4.1), and CP-SAT, which searches over integers with propagation
and clause learning (lesson 4.4.1). Lesson 1.1.3 said CP-SAT "shines on scheduling, sequencing and
dense logic" and promised a measurement. This lesson makes it, on three GridCap-style models chosen
because they pull in different directions: the one-period selection, a vegetation crew's trimming
order, and the ten-year selection of GridCap medium.

A comparison between solvers is easy to get wrong, so the measurements follow three rules. Each
solver gets a **deterministic work limit** instead of a time limit (HiGHS a number of
branch-and-bound nodes; CP-SAT one search worker, or a deterministic portfolio, and a limit in
deterministic time, a work measure the solver keeps "as close as possible to a second"), so a run
gives the same answer every time and on every machine; each run is repeated once to show it. The
programs print statuses, values and bounds, never wall-clock times, which change from machine to
machine and run to run. And the conclusion is about these models: the lesson ends with how to
measure your own.

GridCap is a fictional utility's portfolio, generated for this course; the trimming jobs below are a
seeded random draw in its style.

## The Model

Three models, two of them from earlier lessons.

**The one-period selection** is lesson 4.4.1's model, unchanged.

**The crew's trimming order.** One vegetation crew trims $`n`$ circuits, one at a time.

- *Sets.* $`J = \{1, \dots, n\}`$, the circuits.
- *Parameters.* $`d_j`$, the days circuit $`j`$ takes; $`u_j`$, its due day; $`w_j`$, its risk
  weight (how much a day's lateness costs); $`H = \sum_j d_j`$, the horizon in days.
- *Variables.* $`s_j \in \{0, \dots, H\}`$, the day trimming starts; $`\ell_j \in [0, H]`$, its
  lateness in days; $`y_{jk} \in \{0, 1\}`$ for each pair $`j < k`$, 1 if $`j`$ is trimmed before $`k`$.
- *Objective.* $`\min \sum_{j \in J} w_j\, \ell_j`$, the risk-weighted lateness.
- *Constraints.*

```math
\begin{aligned}
\ell_j &\ge s_j + d_j - u_j && \forall j \in J && \text{(late}_j) \\
y_{jk} = 1 &\Rightarrow s_j + d_j \le s_k && \forall j < k && \text{(before}_{jk}) \\
y_{jk} = 0 &\Rightarrow s_k + d_k \le s_j && \forall j < k && \text{(after}_{jk})
\end{aligned}
```

Each pair is a **disjunction**: one circuit or the other goes first. For HiGHS, each implication is
a big-M row: $`s_j + d_j \le s_k + H(1 - y_{jk})`$ and $`s_k + d_k \le s_j + H\, y_{jk}`$. A big
$`M`$ has to be at least the most the row could be broken by when it is switched off, which comes
from bounds in the data. Here the crew never needs to wait, so every circuit can be finished by day
$`H`$; then $`s_j + d_j - s_k \le H`$, and $`M = H`$ is enough to switch either row off. (Lesson
6.2.1, in section 6, derives such bounds, and lesson 6.2.4 treats disjunctions, in depth.) For CP-SAT
it is the row with `only_enforce_if(y)` or `only_enforce_if(~y)` (lesson 4.4.2). In CP-SAT, $`\ell_j`$ is an integer from 0 to $`H`$; it is a
whole number at the optimum anyway, because every $`d_j`$ and $`u_j`$ is.

**The ten-year selection** is the multi-period timing model of lesson 4.3.1 on GridCap medium:
start-time binaries $`x_{i,t}`$, 1 if project $`i`$ starts in year $`t`$, for each project and
allowed start year, at most one start per project and exactly one for a must-do, at most one
project per alternative group, children starting at least their lag after their parents, and a budget row per year, maximizing NPV by start year. Lesson 4.3.1 states it
in full (without that lesson's reserve rows), and lesson 6.4.1, in section 6, builds it step by
step; it has no logic beyond what those rows say.

## On a Plain Selection Both Prove the Same Optimum

Lessons 4.4.1 and 4.4.2 already ran the comparison on GridCap small's selection, with every rule
variant:

```text
HiGHS OPTIMAL  objective 25,374  same plan: True
```

```text
all five       OPTIMAL  objective 23,775 (-1,599)  HiGHS 23,775  adds ['P013', 'P014', 'P024', 'P036']  drops ['P011', 'P022', 'P029', 'P032']
```

Both solvers proved the same optimum, with no limit set. This is the common
case the OR-Tools guide *Mixed-Integer Programming* describes: for many problems there is no clear
difference in speed, and the choice can come down to which modeling style suits the rules. For
GridCap's rules, that tilts toward CP-SAT's `add_implication` and `only_enforce_if` when the rules
are many and logical, and toward MathOpt when the model must also run on other solvers
(lesson 4.2.3).

<!-- practice 1 -->

## Disjunctions and Sequencing Favor CP-SAT

The crew's trimming order, for 8, 10 and 12 circuits. HiGHS gets 10,000 nodes; CP-SAT one worker and
10 units of deterministic time. The two models differ only in how each disjunction is written:

```python
            first = model.add_binary_variable()                # 1: circuit i is trimmed before j
            model.add_linear_constraint(start[i] + d <= start[j] + horizon * (1 - first))
            model.add_linear_constraint(start[j] + jobs[j][0] <= start[i] + horizon * first)
```

```python
            first = model.new_bool_var(f"first_{i}_{j}")
            model.add(start[i] + d <= start[j]).only_enforce_if(first)
            model.add(start[j] + jobs[j][0] <= start[i]).only_enforce_if(~first)
```

```text
  n  solver status    best plan   bound  repeats
  8  HiGHS  OPTIMAL         100     100  True
  8  CP-SAT OPTIMAL         100     100  True
 10  HiGHS  FEASIBLE        133       0  True
 10  CP-SAT OPTIMAL         133     133  True
 12  HiGHS  FEASIBLE        176       3  True
 12  CP-SAT OPTIMAL         167     167  True
```

With 8 circuits both prove the optimum. With 10, HiGHS finds the optimal order (133) but after 10,000
nodes its bound is still 0: it cannot rule out a plan with no lateness at all. With 12 it has not
found the best order (176 against 167) and its bound is 3. CP-SAT proves every optimum within its
limit. Both runs repeat exactly.

The bound tells you why. In the LP relaxation of the big-M model, $`y_{jk}`$ may be $`0.5`$, and then
both rows read $`s_j + d_j \le s_k + H/2`$ and $`s_k + d_k \le s_j + H/2`$: with $`H`$ as large as
all the trimming days together, both hold with every circuit starting on day 0. The relaxation says
"no lateness is possible", so its bound is near 0 and branching has to fix many $`y`$ before the bound
rises. This is the weak relaxation a big-M row gives, at its worst (lesson 6.2.2, in section 6,
measures what a loose $`M`$ does to the LP bound): the rule is nothing but
disjunctions. CP-SAT does not rely on that relaxation. Once a few orders are decided, propagation
narrows every start day's range, and each dead end teaches it a clause that rules out a whole family
of orders.

So reach for CP-SAT when the model is mostly **logic and disjunctions**: sequencing, scheduling with
"this or that first", many if-then rules, all-different assignments. Lessons 4.5.1 and 4.5.2 go further with
CP-SAT's interval variables and `add_no_overlap`, built for exactly this crew problem.

<!-- practice 2 -->

## Large Models With Strong LP Bounds Favor a MIP Solver

The ten-year selection of GridCap medium is the other kind of model: hundreds of yes/no decisions
tied together by a few budget rows: a multi-dimensional knapsack (yes/no items under several
capacity rows) with timing (lesson 6.3.1, in section 6, treats knapsacks in depth). Its LP
relaxation is close to the integer optimum, which is exactly what branch-and-bound needs. The model
is written once, and `build(portfolio, api)` creates it in either API:

```python
def build(portfolio, api: str):
    """Start-year binaries x[i, t], once/must rows, alternatives, parents with lags, yearly budgets."""
    by_id = {p.project_id: p for p in portfolio.projects}
    if api == "mathopt":
        model = mathopt.Model(name="multi-period")
        new_bool, add = (lambda name: model.add_binary_variable(name=name)), model.add_linear_constraint
    else:
        model = cp_model.CpModel()
        new_bool, add = model.new_bool_var, model.add
```

HiGHS gets 2,000 nodes. CP-SAT gets 10 units of deterministic time twice: once with one worker, and
once with 8 workers running an **interleaved** portfolio, a parameter (`interleave_search`) that
`sat_parameters.proto` describes as deterministic whatever the number of workers (lesson 4.6.3):

```text
GridCap medium: 400 projects, 887 start variables, 10 years
solver                 status     best plan      bound    gap  repeats
HiGHS                  FEASIBLE     226,797    226,914  0.05%  True
CP-SAT, 1 worker       FEASIBLE     224,421    231,151  3.00%  True
CP-SAT, 8 interleaved  FEASIBLE     226,656    226,919  0.12%  True
```

HiGHS ends within 0.05% of its bound. A single CP-SAT worker ends 3% away, with both a worse plan and a
weaker bound. The 8-worker portfolio closes most of that, to 0.12%, but HiGHS on its single search is
still closer. The limits are in different units (nodes, deterministic seconds), so this is not a race
with a winner; it is the shape of the result that matters. On a large model whose LP relaxation is
strong, an LP-based MIP solver gets its bound from the relaxation directly, while CP-SAT has to earn
it, and does so mainly through its LP-based workers (the Primer's chapter on the search describes
them), which is why one worker does much worse than a portfolio.

Also part of "when it doesn't": the free LP bound. HiGHS's best bound comes from LP relaxations at
every node, and it reports duals for an LP (lesson 2.3.3). CP-SAT reports a bound, but no duals, no
reduced costs, and no LP relaxation you can inspect.

## Continuous Amounts Need MathOpt or Scaling

The third limit is the type of variable. CP-SAT's model has no continuous variable at all; its
variable makers are

```text
CpModel variable makers: ['new_bool_var', 'new_int_var', 'new_int_var_from_domain']
```

(intervals aside, lesson 4.5.1). A model with a genuinely continuous quantity, an amount of money
borrowed, a flow, an LP's dual, belongs in MathOpt. MathOpt can still hand such a model to CP-SAT:
lesson 4.4.1's credit line, turned into any amount from $0k to $2,000k at 0.6 $k of cost per $k
borrowed, solved by both:

```python
borrow = model.add_variable(lb=0, ub=2_000, name="borrow")       # continuous, $k
model.add_linear_constraint(k == 0)                               # replace the tranches by the amount
budget = next(c for c in model.linear_constraints() if c.name == "budget")
budget.set_coefficient(borrow, -1)
model.objective.set_linear_coefficient(borrow, -0.6)
```

```text
HIGHS   OPTIMAL  objective 25,435.0  borrow $1,220.0k  21 projects
CP_SAT  OPTIMAL  objective 25,435.0  borrow $1,220.0k  21 projects
from CP-SAT's log: ['Scaling to pure integer problem.']
```

Same answer. The log line shows how: before searching, CP-SAT's MathOpt backend turned the model into
a pure integer one, scaling the continuous variable and the float coefficient. Here that is harmless,
because the best amount is a whole number of $k anyway. On a model where continuous quantities carry
the structure (a network flow, a blend), that conversion is approximate by nature, and an LP-based
solver handles the continuous part directly; keep such models on HiGHS, SCIP or Gurobi, and use
CP-SAT where the decisions are discrete.

## Measure on Your Own Model Before You Choose

The three results give a rule of thumb, and no more:

| Your model is mostly | Likely better | Seen here |
| --- | --- | --- |
| yes/no selection with a few linear rules | either; pick by modeling style | GridCap small: same optimum, both at once |
| logic, disjunctions, sequencing, all-different | CP-SAT | crew order: CP-SAT proves, big-M HiGHS stalls at a bound near 0 |
| large, linear, strong LP relaxation (knapsack-like, flows) | a MIP solver | GridCap medium: HiGHS closest to proven |
| continuous amounts, or a need for duals | a MIP or LP solver through MathOpt | the credit line: CP-SAT must scale it to integers |
| fractional data in the rows | a MIP solver, or CP-SAT after exact scaling (lesson 4.4.3) | |

When the model is in between, measure, and measure fairly:

1. **Write the model once** and build it for each solver, as `multi_period.py` does, so you compare
   solvers rather than two different models.
2. **Use deterministic limits** (a node limit, CP-SAT's deterministic time with one worker or an
   interleaved portfolio) or no limit at all, and repeat each run to confirm it repeats.
3. **Compare statuses, values and bounds**, on several instances of the size you will run in
   production; a single instance can mislead.
4. **Check the plans against each other**: if two solvers prove different optima, one of the models
   is wrong.

Lesson 5.4.2, in section 5, turns this into a benchmark harness with seeds and
time-to-gap; this lesson's job is to know which way to lean before you start.

## Summary

- **On a plain selection both prove the same optimum.** For GridCap's selection, choose by modeling
  style; CP-SAT's logic constraints read like the rules.
- **Disjunctions and sequencing favor CP-SAT.** A big-M disjunction's LP bound is near 0; CP-SAT
  proves optima that HiGHS cannot within the same kind of limit.
- **Large models with strong LP bounds favor a MIP solver.** On GridCap medium's ten-year selection,
  HiGHS ends closest to proven; one CP-SAT worker is far behind, a portfolio much closer.
- **Continuous amounts need MathOpt or scaling.** CP-SAT has no continuous variable; its MathOpt
  backend scales such a model to integers.
- **Measure on your own model before you choose.** One model, deterministic limits, statuses and
  bounds, several instances.

## Reference

| | CP-SAT | MIP solver (HiGHS through MathOpt) |
| --- | --- | --- |
| variables | Booleans and bounded integers | continuous, integer, binary |
| data | whole numbers in rows; floats in the objective | any numbers, within tolerances |
| logic | native: `add_bool_or`, `add_implication`, `only_enforce_if` | linear rows, big-M or indicators (lesson 4.3.1; lessons 6.1.2 and 6.2.1 in section 6) |
| bound | from propagation, clauses and LP workers | from LP relaxations |
| duals, reduced costs | none | yes, for an LP |
| parallel search | a portfolio of workers | depends on the solver |
| shines on | scheduling, sequencing, dense logic | large linear models, continuous parts |

| Fair comparison | How |
| --- | --- |
| same model | one builder, two APIs |
| repeatable runs | node limit for HiGHS; `num_workers = 1` or `interleave_search` and `max_deterministic_time` for CP-SAT |
| what to print | status, value, bound; never wall time from one run |

**Further reading:** [Mixed-Integer Programming (OR-Tools)](https://developers.google.com/optimization/mip)
(MIP solvers for problems that are an LP with integer variables, CP-SAT for problems that are mostly
Boolean, and often no clear difference in speed); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver)
(CP-SAT works over the integers); [`sat_parameters.proto` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)
(`num_workers`, `max_deterministic_time` and `interleave_search`, the deterministic portfolio);
[The CP-SAT Primer, Alternatives (Krupke)](https://d-krupke.github.io/cpsat-primer/big_picture.html)
(when a MIP solver or CP-SAT fits, and CP-SAT's lack of continuous variables); [The CP-SAT Primer, How CP-SAT Reasons: The Search Core (Krupke)](https://d-krupke.github.io/cpsat-primer/search_core.html)
(propagation, clause learning, the LP relaxation as a propagator, and the portfolio of workers);
[The CP-SAT Primer, introduction (Krupke)](https://d-krupke.github.io/cpsat-primer/) (MIP as the most
successful general approach, and where many logical constraints make CP-SAT competitive).

## Challenges

1. Raise HiGHS's node limit in `sequencing.py` to 100,000 for 10 circuits. Predict whether it proves
   the optimum, then run it.
2. Give `multi_period.py`'s single CP-SAT worker 60 units of deterministic time. Predict the gap.
3. Give each start day in the HiGHS model a smaller upper bound you can justify from the data, and
   use it as $`M`$. Does HiGHS's bound after 10,000 nodes rise?

## Design Note: Keep the Model Portable Until You Have Measured

`multi_period.py` builds one model for both APIs from a dozen lines. That is cheap insurance: the
choice of solver is a measurement, not a belief, and the measurement changes when the data grows or a
rule is added. Keep the model in a form that can reach both (MathOpt does this for MIP solvers and
CP-SAT alike, lesson 4.2.3) until the numbers on your own instances settle the choice; then use the
chosen solver's own strengths, such as CP-SAT's `only_enforce_if` or HiGHS's duals, deliberately.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**sequencing.py.** One crew's trimming order as a big-M MILP for HiGHS and as a CP-SAT model with
enforced rows, for 8, 10 and 12 circuits, each run twice (*Disjunctions and Sequencing Favor
CP-SAT*). *Try:* Add 14 circuits. Predict both solvers' statuses.

- Program: [sequencing.py](src/sequencing.py)

**multi_period.py.** GridCap medium's ten-year selection, built once for both APIs and solved by
HiGHS, one CP-SAT worker and an interleaved portfolio (*Large Models With Strong LP Bounds Favor a MIP
Solver*). *Try:* Give HiGHS 200 nodes instead of 2,000. Predict its gap.

- Program: [multi_period.py](src/multi_period.py)

**continuous.py.** CpModel's variable makers, and a continuous credit-line amount solved through
MathOpt by HiGHS and by CP-SAT (*Continuous Amounts Need MathOpt or Scaling*). *Try:* Make
the cost 0.65 $k per $k. Predict the amount borrowed.

- Program: [continuous.py](src/continuous.py)
