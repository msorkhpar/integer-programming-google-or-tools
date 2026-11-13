# 14.2.5 Two Goals: Risk Against NPV

The planning lead read the two plans of the lesson *Value: NPV by start year and risk reduction* and asked for something in between:

> The NPV plan leaves too much risk on the table, and the risk plan gives up $5.7M of NPV. Show us
> the options in between: for each extra bit of risk removed, how much NPV does it cost? And let us
> set a floor on risk removed and get the best NPV above it.

## One Objective Gives One End of the Trade

`steps/04` maximizes one measure, chosen by the request's `objective` setting. Its two plans are
the ends of the trade: the most NPV ($24,260k, removing $3,709k of risk) and the most risk removed
($6,828k, worth $18,559k). The code has no way to ask for a plan between them, because the request
has nowhere to put a floor and the model has no row for one. It also has a weaker flaw at each
end: when two plans tie on the measure that is maximized, the solver returns either, and one of
them may remove less risk for the same NPV.

## A Floor on Risk Turns the Trade Into a Series of NPV Solves

Section 8 offered three ways to trade two goals:

| Method | For | Against |
| --- | --- | --- |
| weighted sum, $`\max\ \text{NPV} + w \cdot \text{risk}`$ (lesson 8.1.1) | one solve per weight | the weight has no unit a planner can set; it finds only supported points (lesson 8.1.2) |
| lexicographic, one goal then the other within a tolerance (lesson 8.2.1) | settles ties at each end | gives one plan, not the trade |
| ε-constraint, $`\max\ \text{NPV}`$ with $`\text{risk} \ge \varepsilon`$ for a series of $`\varepsilon`$ (lesson 8.3.1), each point finished lexicographically (chosen) | the floor is in $k, a number planners can read and set; finds unsupported points too | two solves per point |

The planner uses ε-constraint for the frontier and for the planners' floor, and the lexicographic
second solve for every point, so no point is beaten on one goal by a plan equal on the other
(the weakly efficient points of lesson 8.3.2).

## The Model

The model of the lesson *Value: NPV by start year and risk reduction*, with a risk floor row and the two-solve recipe of each point.

**Sets.** $`P`$, $`Y`$, $`T_i`$, $`M`$, $`\mathcal{G}`$, $`\mathcal{B}`$, $`C`$ as in the lesson *Business rules: must-dos, bundles, parents and alternatives*.

**Parameters.** $`c_{i,k}`$, $`B_y`$, $`\text{npv}_{i,t}`$, $`r_{i,t}`$, $`L_c`$ as in the lesson
*Value: NPV by start year and risk reduction*; $`\varepsilon`$, the floor on risk removed ($k), from the planners or from the frontier's
grid; $`\text{NPV}^*`$, the NPV the first solve found ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$.

Write $`\text{NPV}(x) = \sum_{i,t} \text{npv}_{i,t}\, x_{i,t}`$ and
$`\text{R}(x) = \sum_{i,t} r_{i,t}\, x_{i,t}`$.

**Objective.** First solve, then second solve:

```math
\text{(1)}\ \max\ \text{NPV}(x) \qquad\qquad \text{(2)}\ \max\ \text{R}(x) \ \text{ subject also to (keep\_npv)}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{started}(j) - \text{started}(b_1) &= 0 && \forall B \in \mathcal{B},\ j \in B \setminus \{b_1\} && \text{(bundle}_{b_1,j}) \\
\text{started\_by}(c, t) - \text{started\_by}(p(c), t - L_c) &\le 0 && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\; t \le y < t + d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\text{R}(x) &\ge \varepsilon && && \text{(risk\_floor)} \quad \leftarrow \text{new, when a floor is set} \\
\text{NPV}(x) &\ge \text{NPV}^* - 0.5 && && \text{(keep\_npv)} \quad \leftarrow \text{new, second solve only}
\end{aligned}
```

NPVs are whole $k, so two plans with different NPV differ by at least 1, and a slack of 0.5 keeps
the first solve's NPV without depending on the solver's last digit. For the risk end the roles
swap: maximize $`\text{R}`$, then $`\text{NPV}`$ with $`\text{R}(x) \ge \text{R}^* - 10^{-6}`$
(`keep_risk`), a tiny slack because risk is a float sum.

The frontier's floors are spread evenly between the risk removed by the NPV end,
$`\text{R}^{\text{lo}}`$, and the risk removed by the risk end, $`\text{R}^{\text{hi}}`$. For
$`n`$ points, the $`n - 2`$ floors between the ends are

```math
\varepsilon_k = \text{R}^{\text{lo}} + k \, \frac{\text{R}^{\text{hi}} - \text{R}^{\text{lo}}}{n - 1}, \qquad k = 1, \dots, n - 2
```

## The Change, File by File

**`cipt/model.py`.** Before (step 04), the rules ran first and the value expressions were built
after them. The risk floor is a rule on `built.risk`, so the order had to flip. From
`steps/05/cipt/model.py`:

<!-- snapshot: steps/05/cipt/model.py -->
```python
    built = Built(request, model, x)
    value = coefficients(request)
    built.npv = mathopt.fast_sum(value[key][0] * v for key, v in x.items())
    built.risk = mathopt.fast_sum(value[key][1] * v for key, v in x.items())
    for rule in RULES:
        rule(built)
```

A rule may now use the measures. That is a small, real constraint on the design: the value layer
must be complete before any rule runs.

**`cipt/rules.py`.** One rule, added to `RULES`. From `steps/05/cipt/rules.py`:

<!-- snapshot: steps/05/cipt/rules.py -->
```python
def risk_floor(built: Built) -> None:
    """(risk_floor) the plan removes at least the floor the planners set, when they set one."""
    if built.request.risk_floor is not None:
        built.add("risk_floor", built.risk >= built.request.risk_floor)
```

**`cipt/data.py`.** `Request` gains `risk_floor: float | None`, read from the request's
`risk_floor` setting; `None` means no row.

**`cipt/solve.py`.** `solve(request)` split in two, so other code can change a built model before
solving it. From `steps/05/cipt/solve.py`:

<!-- snapshot: steps/05/cipt/solve.py -->
```python
def solve_built(built: Built) -> Plan:
    """Solve a model the caller may have changed (a new objective, an extra row) after `build`."""
    return read_plan(built, run_highs(built.model))
```

**`cipt/goals.py`.** Before: the stub of the lesson *Value: NPV by start year and risk reduction*, `frontier` returning an empty list,
with the record `Point` already in place. After, the file starts with the two slacks and that
record. From `steps/05/cipt/goals.py`:

<!-- snapshot: steps/05/cipt/goals.py -->
```python
#: Slack on a goal a second pass must keep: NPV is whole $k; risk is a float sum.
KEEP = {"npv": 0.5, "risk": 1e-6}


@dataclass(frozen=True)
class Point:
    npv: float
    risk: float
    plan: Plan
```

`KEEP` holds the slack of `keep_npv` and `keep_risk`, keyed by the goal the second solve keeps. A
`Point` is one plan of the frontier with its two values, its NPV and the risk it removes, in $k.
Two functions of `steps/05/cipt/goals.py` do the work. `best(request, first, floor=None)` is the
two-solve recipe of one point, and the page leaves its code to the practice. `first` names the
goal of the first solve, `"npv"` or `"risk"`; the other goal is the one `first` does not name.

1. Build the model once. When a `floor` is given, add the row $`\text{risk\_floor}`$ of the model
   above, $`\text{R}(x) \ge \varepsilon`$ with $`\varepsilon`$ the `floor`, under the name
   `risk_floor`.
2. Maximize the `first` goal, solve (1) of the model above, with `solve_built`. A plan whose status
   is not `"optimal"` is returned as it is.
3. Otherwise add the keep row: $`\text{keep\_npv}`$ when `first` is `"npv"`, which holds the goal
   at least at the first solve's value minus its slack in `KEEP`, under the name `keep_<first>`.
   For `first` set to `"risk"` it is `keep_risk`, the same row on $`\text{R}`$ with the risk slack.
   The first solve's value is the plan's `npv` or `risk`.
4. Maximize the other goal, solve (2), and return that plan.

The second solve reuses the same `Built`: one row added, the objective replaced. `frontier` calls
`best` for each end and each floor, in this order: the NPV end, the floors from low to high, the
risk end. From `steps/05/cipt/goals.py`:

<!-- snapshot: steps/05/cipt/goals.py -->
```python
    ends = [best(request, "npv"), best(request, "risk")]
    if any(p.status != "optimal" for p in ends):
        return []
    low, high = ends[0].risk, ends[1].risk
    plans = [ends[0]]
    for k in range(1, points - 1):
        plans.append(best(request, "npv", floor=low + k * (high - low) / (points - 1)))
    plans.append(ends[1])
```

Then it drops points in two passes, repeats first. A plan is kept when it is optimal and its NPV is
not within 0.5 of a point already kept; of two plans with the same NPV, the earlier in the order
above stays. Only then are dominated points dropped, among the points the first pass kept. From
`steps/05/cipt/goals.py`:

<!-- snapshot: steps/05/cipt/goals.py -->
```python
    found: list[Point] = []
    for plan in plans:
        point = Point(plan.npv, plan.risk, plan)
        if plan.status == "optimal" and not any(abs(point.npv - q.npv) <= KEEP["npv"] for q in found):
            found.append(point)
    return [p for p in found if not any(dominates(q, p) for q in found)]
```

`dominates(a, b)` is true when `a` is at least as good as `b` on both goals and better on one, each
comparison within that goal's slack in `KEEP`. The frontier comes out in the order the plans were
found, from the best NPV to the most risk removed.

**`cipt/diagnose.py`** is new and is the stub for the lesson *Why it failed, why it was deferred: a diagnostics layer*.
No code of this step imports it, and in this lesson's practice it is already this stub.

## Five Points Show Where Risk Gets Expensive

`frontier_small.py` asks `steps/05` for five points on GridCap small (a fictional utility):

```text
frontier of GridCap small, five points requested:
   NPV ($k)   risk removed ($k)   funded   NPV given up per $k of risk
     24,260             3,709.1       27                              
     24,148             4,600.5       27                          0.13
     23,926             5,335.3       29                          0.30
     23,013             6,371.8       31                          0.88
     18,878             6,827.9       32                          9.07
```

The last column is the price of the next step: from the NPV end, $891k more risk removed costs
$112k of NPV, $0.13 per dollar of risk. The last step costs $9.07 per dollar. A planner reads it
at once: the first three points are cheap, and the risk end is not worth its price unless risk is
the mandate.

The risk end is worth $18,878k here, against $18,559k for the step-04 risk plan. Both remove the
same $6,827.9k of risk; the lexicographic second solve found $319k more NPV among the plans that
tie on risk. That is the weak point of lesson 8.3.2, on real data.

The same program runs the weighted sum for comparison:

```text
weighted sum NPV + w * risk, w -> (NPV, risk): 0 -> (24,260, 3,709.1); 0.5 -> (24,069, 5,177.5); 1 -> (22,966, 6,501.4)
  2 -> (22,882, 6,562.8); 5 -> (22,448, 6,660.5); 100 -> (18,878, 6,827.9)
```

The weights found four plans the five-point grid did not, (24,069, 5,177.5) among them: five
floors are a sample of the frontier, not all of it. A planner who wants more points asks for more,
at two solves each. What the weights cannot give is a plan for a stated floor: no weight in the list
answers "at least $5,000k of risk".

## A Floor Is a Request Setting, So the Planners Can Ask for It

`risk_floor` lives in the request, so a planner sets it beside the export and gets one plan, by
the ordinary `solve`. From `steps/05/tests/test_goals.py`, on three projects where any two fit:

<!-- snapshot: steps/05/tests/test_goals.py -->
```python
def test_risk_floor_is_respected():
    plan = solve(load_request(three(risk_floor=300)))
    assert (plan.funded, round(plan.npv)) == (("A", "C"), 400)
```

```text
14.2.5: 5 tests added; on step 04, 5 fail on an assertion; on step 05, 33 of 33 pass
  test_frontier_runs_from_best_npv_to_most_risk_removed
    before: assert [] == [500, 400, 300]
    after:  passed
  test_frontier_finds_the_plan_between_the_ends
    before: assert [] == [('A', 'B'), ...), ('B', 'C')]
    after:  passed
  test_no_frontier_point_is_dominated
    before: assert 0 >= 2
    after:  passed
  test_tied_npv_end_takes_the_most_risk
    before: assert [] == [('B',)]
    after:  passed
  test_risk_floor_is_respected
    before: assert (('A', 'B'), 500) == (('A', 'C'), 400)
    after:  passed
```

`test_tied_npv_end_takes_the_most_risk` gives two projects the same NPV and very different risk;
only one fits. A single NPV solve may return either. The test passes only if the second solve
picks the riskier asset's project, whichever the first solve returned. Every test compares a list
(`[] == [...]`) rather than indexing into it, so the stub's empty frontier fails on an assertion
instead of an `IndexError`.

## Two Goals Cost One File and One Reordering

```text
14.2.5: steps/04 -> steps/05
  package lines 324 -> 390, functions 31 -> 37, tests 28 -> 33
  most branches: data.load_request (10) -> goals.frontier (10)
  data.py       105 ->  106
  diagnose.py     0 ->   20
  goals.py       13 ->   52
  rules.py       42 ->   46
  solve.py       36 ->   38
```

The model file did not grow: the change there was the order of two blocks. `goals.py` holds the
method, and it only calls `build`, `add`, `maximize` and `solve_built`, the same calls a planner's
script could make. `frontier` is now the most-branched function, with its loops, comprehensions and
guards; it is a candidate for splitting if it grows again.

**Practice.** This lesson's project practice starts from `steps/04`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds. This step's `main.py` also
prints the frontier of the demo export after the report: an empty line, the line
`NPV against risk removed:`, then one line per point, from the best NPV to the most risk removed,
as `  NPV $<npv>k  risk removed $<risk>k  funds <ids>` (two spaces between the parts, NPV in whole
$k and risk with one decimal, both with thousands commas, the funded ids in id order separated by
a comma and a space).

<!-- practice 1 -->

## Summary

- **One objective gives one end of the trade.** The step-04 code could not ask for a plan between
  the ends, and settled ties at each end by chance.
- **A floor on risk turns the trade into a series of NPV solves** (ε-constraint), each finished by
  a lexicographic second solve.
- **Five points show where risk gets expensive**: $0.13 of NPV per $1 of risk at first, $9.07 at
  the end, on GridCap small.
- **A floor is a request setting**, so planners ask for it without code.

## Reference

| Name | Meaning |
| --- | --- |
| `risk_floor` (row and setting) | $`\text{R}(x) \ge \varepsilon`$ |
| `keep_npv`, `keep_risk` | the second solve keeps the first solve's value, within 0.5 or $`10^{-6}`$ |
| `best(request, first, floor)` | the two-solve recipe of one point |
| `frontier(request, points)` | the ends and $`n - 2`$ floors, repeated and dominated points dropped |
| `dominates(a, b)` | $`a`$ at least as good on both goals and better on one, within the slacks |

**Further reading:** [MathOpt `model.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`maximize` replaces the objective of a built model, which the second solve relies on); [MathOpt `expressions.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/expressions.py) (`evaluate_expression`, which gives each plan both of its values).

## Challenges

1. Ask for nine points instead of five. Predict how many survive the dominance filter, then run it.
2. The planners want a floor on NPV and the most risk above it. Which two lines of `best` change?
3. Why is `keep_npv`'s slack 0.5 and not 0? Construct a case where 0 would make the second solve
   infeasible on a solver that returns 24,259.9999.

## Design Note: A Method Outside the Model

`goals.py` builds no rows of its own kind; it adds ordinary rows and changes the objective of a
model that `build` made. Putting the frontier inside `build` (a flag that returns many models) would
have mixed the question "what are the rules" with "what are we asking". Keeping methods outside
means a new question (a frontier on NPV against capex, say) is a new function in a new file, and
`model.py` does not change.

## The Full Programs

**frontier_small.py.** Five frontier points on GridCap small with `steps/05`, and six weighted sums
for comparison. *Try:* add `w = 0.25` to the weights and predict whether it finds a new plan.

- Program: [frontier_small.py](src/frontier_small.py)

**ledger.py, code_size.py.** The test ledger and the size table for step 05.

- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
