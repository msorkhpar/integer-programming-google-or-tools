# 3.2.1 Branching on a Fractional Variable

GridCap's planners send the tiny portfolio to HiGHS: eight candidate projects, a $7,390k capital
budget, one must-do project, one project that needs another, and two projects that are alternatives
to each other. HiGHS answers: fund P001, P002, P005 and P006, worth $3,627k. There are
$`2^8 = 256`$ yes/no plans, so trying them all would have worked here. For the small portfolio's 40
projects there are about $`1.1 \times 10^{12}`$, and for the medium portfolio's 400 the number has
121 digits. HiGHS does not try them all. It runs **branch-and-bound**, the method at the core of
MILP solvers, and this module builds it by hand.

Branch-and-bound rests on one move: solve an LP, find a variable the LP set to a fraction, and split
the problem in two on that variable. This lesson takes that move apart in five rules, then repeats
it until the tiny problem is solved.

## The Model

The one-period selection model of lesson 1.1.3, the model HiGHS solved above.

**Sets.** $`P`$, the candidate projects (P001 to P008 on tiny); $`M \subseteq P`$, the must-do
projects; $`C \subseteq P`$, the projects that need a parent project, with $`p(c)`$ the parent of
$`c`$; $`\mathcal{G}`$, the alternative groups, each a set of projects of which at most one may be
funded.

**Parameters.** $`c_i`$, the capex of project $`i`$ ($k); $`v_i`$, its value, the NPV if it starts
as early as it can ($k); $`B`$, the capital budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

**Objective.**

```math
\max \; \sum_{i \in P} v_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} c_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The code names the rows `budget`, `must_P002`, `parent_P004` and `alt_G006`. Here is the tiny
portfolio's data, which the rest of the module uses:

```text
tiny portfolio, capital budget $7,390k
  P001  capex 2,150  value 1,386
  P002  capex 2,730  value   871  must-do
  P003  capex 2,470  value   576
  P004  capex 3,000  value 2,120  needs P003
  P005  capex   250  value   123
  P006  capex 1,970  value 1,247  group G006
  P007  capex   290  value   265  group G006
  P008  capex   580  value   137
```

So $`M = \{P002\}`$, $`C = \{P004\}`$ with $`p(P004) = P003`$, and
$`\mathcal{G} = \{\{P006, P007\}\}`$. GridCap is a fictional utility's portfolio, made up for
this course. The module's
library `selection.py` builds this model for any GridCap portfolio:

```python
def build(portfolio: Portfolio, integer: bool = False, yearly: bool = False) -> Selection:
    model = mathopt.Model(name=f"{portfolio.name}-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    if yearly:
        for year in portfolio.years:
            model.add_linear_constraint(
                sum(p.spend(p.earliest_start).get(year, 0) * x[p.project_id] for p in portfolio.projects)
                <= portfolio.budget[year], name=f"budget_{year}")
    else:
        model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                    <= portfolio.capital_budget, name="budget")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for group, members in groups.items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{group}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(model, x)
```

With `integer=True` each $`x_i`$ is a whole number between 0 and 1, so 0 or 1: the MILP. With the
default `integer=False` each $`x_i`$ may be any number in $`[0, 1]`$, which is the next rule's
subject. The `yearly` switch replaces the one budget row by a row per year; lesson 3.2.3 uses it,
and it is off until then.

## Dropping Integrality Gives an LP Whose Value Bounds Every Plan From Above

Replace $`x_i \in \{0, 1\}`$ by $`0 \le x_i \le 1`$ and keep every row. The result is an LP, the
**LP relaxation** of the model ("relaxed" because one rule was loosened, not changed). An LP is
what GLOP solves (section 2). Solved, next to the MILP:

```python
lp = solve_lp(build(tiny), fixed={})
print(f"LP relaxation (GLOP): value {lp.value:,.1f}")
for pid, v in lp.x.items():
    print(f"  x_{pid} = {v:.3f}")

milp = solve_milp(build(tiny, integer=True))
print(f"MILP (HiGHS): value {milp.objective_value():,.0f}")
```

```text
LP relaxation (GLOP): value 3,770.1
  x_P001 = 1.000
  x_P002 = 1.000
  x_P003 = 0.099
  x_P004 = 0.099
  x_P005 = 0.000
  x_P006 = 1.000
  x_P007 = 0.000
  x_P008 = 0.000
MILP (HiGHS): value 3,627
the LP value is 143.1 above the best plan
```

The LP's value, 3,770.1, is higher than the best real plan's 3,627. It always is at least as high,
because every allowed plan is also a point of the relaxation (lesson 3.1.2 gives the argument). For
a maximization:

```math
z_{\text{LP}} \;\ge\; z_{\text{MILP}}
```

That inequality is the "bound" in branch-and-bound. An LP value is an **upper bound**: a number no
plan can beat. The gap between the two, here 143.1, is the **integrality gap**; lesson 3.1.2 measures it across GridCap. This lesson needs only its sign.

## A Fractional Value Marks the Variable to Branch On

An LP solution whose variables are all 0 or 1 is a real plan, and by the inequality above it is
then the best plan: nothing beats the LP, and this plan reaches the LP's value. The tiny LP is not
that lucky. Two variables are fractions: $`x_{P003} = x_{P004} = 0.099`$.

The fraction has a plain reading. P001, P002 and P006 cost 6,850, which leaves 540 of the 7,390.
P007 would be the best use of it, but it is P006's alternative. Next is P004, which needs P003, so
the row parent$`_{P004}`$ makes the LP buy the two together: 5,470 of capex for 2,696 of value,
$`2{,}696 / 5{,}470 = 0.493`$ per dollar, a hair above P005's $`123 / 250 = 0.492`$. The LP spends
the 540 on that pair and buys $`540 / 5{,}470 = 0.099`$ of it. A planner cannot fund 9.9% of a tower replacement, and
rounding does not rescue the plan. Rounding both up costs $`6{,}850 + 5{,}470 = 12{,}320`$, far over
budget; rounding both down gives P001, P002 and P006, worth 3,504, a real plan but not the best one
(lesson 3.1.1 shows this failure in general).

A variable whose LP value is not a whole number is **fractional**, and it is where branching starts.
Solvers compute values in floating point, so "not a whole number" has to allow for noise: a value
of 0.9999999 is 1 that picked up rounding error, not a fraction. The library calls a value
fractional when it is more than $`\varepsilon = 10^{-6}`$ away from the nearest whole number:

```python
EPS = 1e-6


def fractional(x: dict[str, float]) -> list[str]:
    """The variables whose LP value is not within EPS of a whole number, in model order."""
    return [name for name, v in x.items() if abs(v - round(v)) > EPS]
```

`round(v)` is the nearest whole number, so the test also works for a variable that may take values
above 1 (a count of crews, later in this lesson). On the root LP it returns `["P003", "P004"]`.
MILP solvers apply the same kind of tolerance to the plans they return, which is why lesson 6.4.1
reads a 0-1 variable as "funded" when its value is above 0.5 rather than equal to 1.

<!-- practice 1 -->

## Branching Splits the Problem Into Two Children That Keep Every Integer Plan

Pick one fractional variable, say $`x_{P003} = 0.099`$. Every real plan has $`x_{P003} = 0`$ or
$`x_{P003} = 1`$, nothing in between. So the problem splits into two smaller problems, called
**children**:

```math
\text{down child: the model} + \{x_{P003} = 0\}, \qquad
\text{up child: the model} + \{x_{P003} = 1\}
```

The split is **branching**, and $`x_{P003}`$ is the **branching variable**. It has three properties,
and all of branch-and-bound depends on them.

1. **No real plan is lost.** Each allowed plan sits in exactly one child, so the best plan overall
   is the better of the two children's best plans.
2. **The fractional LP point is cut off.** The point with $`x_{P003} = 0.099`$ is in neither child,
   so neither child's LP can return it again. The search cannot repeat itself.
3. **Each child is smaller.** It has one more variable fixed, so after at most $`|P|`$ splits on a
   path, every variable is fixed and nothing is left to split.

Each child can be split again, and its children too. Drawn out, the problems form a **search
tree**: the original problem is the **root** at the top, each problem is a **node**, and a node's
children hang below it. A node's **depth** is the number of splits between it and the root, which
for 0-1 variables is the number of variables it has fixed.

A program checks the first property on tiny by listing all 256 plans and keeping the allowed ones:

```python
plans = [dict(zip(ids, bits)) for bits in product((0, 1), repeat=len(ids))]
good = [x for x in plans if allowed(x)]
down = [x for x in good if x["P003"] == 0]
up = [x for x in good if x["P003"] == 1]
print(f"allowed plans: {len(good)} = {len(down)} with x_P003 = 0 + {len(up)} with x_P003 = 1")
print(f"best plan with x_P003 = 0: {max(map(value, down)):,}; with x_P003 = 1: {max(map(value, up)):,}")
```

```text
allowed plans: 32 = 22 with x_P003 = 0 + 10 with x_P003 = 1
best plan with x_P003 = 0: 3,627; with x_P003 = 1: 2,833
```

`allowed` checks the four kinds of rows on a 0-1 plan. Of the 256 plans only 32 obey every row, and
the split puts 22 in one child and 10 in the other, none in both and none in neither. The best plan
overall, 3,627, is the better of the two children's bests. Branch-and-bound never lists plans like
this; the listing only shows that branching keeps every plan somewhere.

## Each Child Is the Same LP With One Bound Changed

Writing "the model plus $`x_{P003} = 0`$" needs no new row. The relaxation already has the bounds
$`0 \le x_{P003} \le 1`$; the down child lowers the upper bound to 0, and the up child raises the
lower bound to 1. So a node of the search is just a list of fixings, and solving it means setting
bounds and calling the LP solver again:

```python
def solve_lp(sel: Selection, fixed: dict[str, int]) -> LP:
    """The relaxation with each variable in `fixed` held at its 0 or 1; the others stay in [0, 1]."""
    for pid, var in sel.x.items():
        var.lower_bound = fixed.get(pid, 0)
        var.upper_bound = fixed.get(pid, 1)
    result = mathopt.solve(sel.model, mathopt.SolverType.GLOP)
    reason = result.termination.reason
    if reason == mathopt.TerminationReason.INFEASIBLE:
        return LP("infeasible", None, {})
    if reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"GLOP stopped with {reason.name}")
    return LP("optimal", result.objective_value(), {pid: result.variable_values(v) for pid, v in sel.x.items()})
```

The model is built once; only the bounds change between nodes. A child's LP can be **infeasible**:
fixings can contradict a row, for example two projects fixed at 1 whose capex is over budget. Then
the child holds no plan at all. Solving the two children of the root:

```python
for name, fixed in (("down child, x_P003 = 0", {"P003": 0}), ("up child,   x_P003 = 1", {"P003": 1})):
    lp = solve_lp(sel, fixed)
    shown = ", ".join(f"{pid} {v:.3f}" for pid, v in lp.x.items() if v > 1e-9)
    print(f"{name}: LP {lp.value:,.1f}  [{shown}]")
```

```text
down child, x_P003 = 0: LP 3,695.5  [P001 1.000, P002 1.000, P005 1.000, P006 1.000, P008 0.500]
up child,   x_P003 = 1: LP 3,054.7  [P002 1.000, P003 1.000, P004 0.633, P007 1.000]
```

Both children's values are below the root's 3,770.1, and they always will be at most the parent's:
a child's LP has the parent's rows and one tighter bound, so its allowed set is a part of the
parent's, and the best over a part is never better than the best over the whole. Going down the
tree, bounds only fall.

Each child is still fractional, on a different variable. The down child takes half of P008, which
now fits; the up child, having paid for P003 (worth only 576), takes 63.3% of P004. So each child
splits again.

## A General Integer Branches on Floor and Ceiling

GridCap's selection variables are 0-1, but a MILP can also have integer variables with larger
ranges: a number of crews, of trucks, of transformer units. For such a variable with fractional LP
value $`v`$, the two children are

```math
\text{down: } x \le \lfloor v \rfloor, \qquad \text{up: } x \ge \lceil v \rceil
```

where $`\lfloor v \rfloor`$ (floor) is the largest whole number not above $`v`$ and
$`\lceil v \rceil`$ (ceiling) the smallest not below it. No whole number lies strictly between them,
so the three properties hold as before. For a 0-1 variable, floor is 0 and ceiling is 1, which gives
$`x = 0`$ and $`x = 1`$: the 0-1 split is the special case.

A small example shows it. A storm-hardening push hires whole contract crews: $`a`$ line crews,
each removing 5 risk points, and $`b`$ tree crews, each removing 8. There are 6 trucks, and the
crews cost $50k and $90k from a $450k budget:

```math
\begin{aligned}
\max \;& 5a + 8b \\
\text{s.t. }& a + b \le 6 && \text{(trucks)} \\
& 50a + 90b \le 450 && \text{(budget)} \\
& a,\ b \in \{0, 1, \dots, 6\}
\end{aligned}
```

The program keeps both variables' bounds in a dict and makes the two children of a node like this:

```python
def children(bounds: dict, name: str, v: float) -> list[tuple[str, dict]]:
    """Down child: name <= floor(v). Up child: name >= ceil(v). Nothing strictly between is lost."""
    lo, hi = bounds[name]
    return [(f"{name} <= {math.floor(v)}", {**bounds, name: (lo, math.floor(v))}),
            (f"{name} >= {math.ceil(v)}", {**bounds, name: (math.ceil(v), hi)})]
```

Each child keeps the other end of the range it had: the down child keeps its lower bound, the up
child its upper bound. It then branches until no LP is fractional, taking $`b`$ when both are:

```text
root: LP 41.25 at (a = 2.25, b = 3.75)
  b <= 3: LP 39 at (a = 3, b = 3)  integral
  b >= 4: LP 41 at (a = 1.8, b = 4)
    a <= 1: LP 40.5556 at (a = 1, b = 4.44444)
      b <= 4: LP 37 at (a = 1, b = 4)  integral
      b >= 5: LP 40 at (a = 0, b = 5)  integral
    a >= 2: infeasible
```

Two things are new here. The variable $`b`$ is branched on twice on one path, first $`b \ge 4`$
and later $`b \le 4`$ against $`b \ge 5`$: with a general integer, one split narrows the range
without fixing the variable. And the node $`a \ge 2`$ is infeasible: with $`b \ge 4`$ and
$`a \ge 2`$, the budget needs at least $`100 + 360 = 460`$. The best integral leaf is $`(0, 5)`$,
worth 40, and the root LP's 41.25 was an upper bound on it, as the first rule promised.

The crew numbers are not new. They are the worked example of MIT's chapter on integer programming
(section 9.5, see Further reading), $`\max 5x_1 + 8x_2`$ subject to $`x_1 + x_2 \le 6`$ and
$`5x_1 + 9x_2 \le 45`$, with the money row multiplied by 10. Its enumeration tree has the same seven
subproblems as the tree above (its $`L_0`$ to $`L_6`$), with the same LP values, so you can check this
program's tree against a drawing.

<!-- practice 2 -->

## Branching Stops at a Node Whose LP Is Infeasible or Integral

Two kinds of node need no more splitting. An **infeasible** node holds no plan, so there is nothing
below it to find. An **integral** node, one whose LP solution has no fractional variable, holds a
real plan, and that plan is the best one in the node: no plan in the node beats the node's LP, and
this plan reaches it. Either way the node is a **leaf**. Every other node is split on a fractional
variable.

The library function `branch_and_bound` does the splitting. Its core lines:

```python
lp = solve_lp(sel, node.fixed)
if lp.status == "infeasible":
    action = "pruned: infeasible"
elif not fractional(lp.x):
    if search.value is None or lp.value > search.value + EPS:
        search.value, search.plan = lp.value, [n for n, v in lp.x.items() if v > 0.5]
        action = f"integral: new incumbent {lp.value:,.0f}"
    else:
        action = f"integral: {lp.value:,.0f} is no better"
else:
    name = choose_variable(sel, node, lp, var_rule, search)
    action = f"branch on x_{name} = {lp.x[name]:.3f}"
    for value in (0, 1):
        waiting.push(Node(made, node.depth + 1, {**node.fixed, name: value}, lp.value, f"x_{name} = {value}"))
        made += 1
```

A node's `fixed` is its parent's fixings plus one, so a node deep in the tree carries every
decision on the path from the root. `waiting` holds the nodes made but not yet solved; this run
always takes the newest one next, and lesson 3.2.3 is about that choice. Each child also stores
its parent's LP value as its `bound`, which lesson 3.2.2 puts to use. The best integral leaf so far
is kept in `search.value` and `search.plan`; the output calls it the **incumbent**, a term lesson
3.2.2 develops. `choose_variable` with its default rule returns
the first fractional variable in project order. To **prune** a node is to stop the search below it;
the word is used for every kind of leaf.

Run on tiny with `prune=False`, which switches off the one kind of pruning that lesson 3.2.2 adds,
the whole tree prints. Each line is a node: its number, its fixing, its LP value and what happened.
Indentation is depth.

```text
  0 root                        LP 3,770.1  branch on x_P003 = 0.099
  2   x_P003 = 1                LP 3,054.7  branch on x_P004 = 0.633
  4     x_P004 = 1              infeasible  pruned: infeasible
  3     x_P004 = 0              LP 2,936.8  branch on x_P001 = 0.884
  6       x_P001 = 1            LP 2,869.6  branch on x_P007 = 0.138
  8         x_P007 = 1          infeasible  pruned: infeasible
  7         x_P007 = 0          LP 2,858.3  branch on x_P006 = 0.020
 10           x_P006 = 1        infeasible  pruned: infeasible
  9           x_P006 = 0        LP 2,852.7  branch on x_P005 = 0.160
 12             x_P005 = 1      infeasible  pruned: infeasible
 11             x_P005 = 0      LP 2,842.4  branch on x_P008 = 0.069
 14               x_P008 = 1    infeasible  pruned: infeasible
 13               x_P008 = 0    LP 2,833.0  integral: new incumbent 2,833
  5       x_P001 = 0            LP 2,802.2  branch on x_P005 = 0.880
 16         x_P005 = 1          LP 2,799.5  branch on x_P006 = 0.982
 18           x_P006 = 1        infeasible  pruned: infeasible
 17           x_P006 = 0        LP 1,972.0  integral: 1,972 is no better
 15         x_P005 = 0          LP 2,746.0  branch on x_P008 = 0.379
 20           x_P008 = 1        LP 2,620.6  branch on x_P006 = 0.786
 22             x_P006 = 1      infeasible  pruned: infeasible
 21             x_P006 = 0      LP 1,849.0  integral: 1,849 is no better
 19           x_P008 = 0        LP 2,694.0  integral: 2,694 is no better
  1   x_P003 = 0                LP 3,695.5  branch on x_P008 = 0.500
 24     x_P008 = 1              LP 3,617.6  branch on x_P006 = 0.976
 26       x_P006 = 1            LP 3,615.2  branch on x_P001 = 0.981
 28         x_P001 = 1          infeasible  pruned: infeasible
 27         x_P001 = 0          LP 2,378.0  integral: 2,378 is no better
 25       x_P006 = 0            LP 2,782.0  integral: 2,782 is no better
 23     x_P008 = 0              LP 3,627.0  integral: new incumbent 3,627
29 nodes, 15 leaves; best integral leaf 3,627: P001, P002, P005, P006
```

Read the first path. The root is split on $`x_{P003}`$, and the up child (node 2) is taken first.
It is split on $`x_{P004}`$; node 4 fixes P004 too, and P002 + P003 + P004 cost 8,200, over budget,
so it is infeasible. Node 3 drops P004 and the path goes on, fixing one project per level, until
node 13 is integral at 2,833: P001, P002 and P003. Only then does the search come back up and take
the down children it left waiting, and the last one, node 23, is the best plan, 3,627, the value
HiGHS returned.

The tree has 29 nodes, against 256 plans. It is smaller because a leaf ends a whole subtree: node
4 is infeasible, so none of the plans that fund P002, P003 and P004 together is ever looked at.
Notice also how much of the work happened below node 2, whose LP value was 3,054.7. Once node 13
had found a plan worth 2,833 and node 23 one worth 3,627, nothing below a node with LP 3,054.7 could
win. Lesson 3.2.2 turns that observation into the rule that gives branch-and-bound its name.

## Summary

- **Dropping integrality gives an LP whose value bounds every plan from above.** Every allowed
  plan is a point of the relaxation, so $`z_\text{LP} \ge z_\text{MILP}`$ for a maximization.
- **A fractional value marks the variable to branch on.** Test the distance to the nearest whole
  number against a tolerance, never `0 < v < 1` with exact floats.
- **Branching splits the problem into two children that keep every integer plan.** Every plan is in
  exactly one child, the fractional LP point is in neither, and each child has one more fixing.
- **Each child is the same LP with one bound changed.** A child's LP value is never above its
  parent's.
- **A general integer branches on floor and ceiling:** $`x \le \lfloor v \rfloor`$ or
  $`x \ge \lceil v \rceil`$.
- **Branching stops at a node whose LP is infeasible or integral.** An integral LP solution is the
  best plan in its node.

## Reference

| Term | Meaning |
| --- | --- |
| LP relaxation | the model with $`x_i \in \{0,1\}`$ replaced by $`0 \le x_i \le 1`$ |
| upper bound | a value no allowed plan can beat; $`z_\text{LP}`$ is one for a maximization |
| fractional variable | LP value more than $`\varepsilon`$ from the nearest whole number |
| branching on $`x_j = v`$ | down child $`x_j \le \lfloor v \rfloor`$, up child $`x_j \ge \lceil v \rceil`$ |
| node | the relaxation plus the fixings on its path from the root |
| leaf | a node that is not split: infeasible, integral, or (lesson 3.2.2) pruned by bound |
| prune | stop searching below a node |

| Tiny result | Value |
| --- | --- |
| root LP relaxation | 3,770.1, with $`x_{P003} = x_{P004} = 0.099`$ |
| children of $`x_{P003}`$ | down 3,695.5, up 3,054.7 |
| best plan (HiGHS and the full tree) | 3,627: P001, P002, P005, P006 |
| full tree without bound pruning | 29 nodes, 15 leaves |

**Further reading:** [Solving a MIP Problem (OR-Tools)](https://developers.google.com/optimization/mip/mip_example) (a two-variable MIP whose LP answer is fractional, the starting point of a branch); [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (the solvers MathOpt calls and the model features it lists, SOS constraints among them); [Mixed-Integer Programming (OR-Tools)](https://developers.google.com/optimization/mip) (OR-Tools' MIP solvers are branch-and-bound solvers); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.5 branches the crew example by hand, and section 9.6 branches only on the integer variables of a mixed model); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2.2: the root LP relaxation, branching on a fractional integer variable with floor and ceiling, and the tree that results).

## Challenges

1. Branch the tiny root on $`x_{P004}`$ instead of $`x_{P003}`$. One child is infeasible. Which
   one, and which rows make it so?
2. In the crew example, branch on $`a`$ first at the root. Draw the tree you expect, then change
   `split[-1]` to `split[0]` in `crew_branch.py` and compare.
3. A variable has LP value $`-1.5`$ (a change in crew count, which may be negative). Write its two
   children. What would `int(v)` give instead of $`\lfloor v \rfloor`$, and which plans would that
   lose?

## Design Note: Why Branch on Variables and Not on Something Else

Any split that sends every plan to one side and the fractional point to neither side would do. A
solver could split on a sum, for example $`x_{P003} + x_{P004} \le 0`$ against
$`x_{P003} + x_{P004} \ge 1`$, or on the budget row. Splitting on one variable is the common
default because it is cheap to apply (two bound changes, no new rows), it keeps the LP the same
size, and its children are easy to name in a log. Branching on a sum of variables in a group, such
as an alternative group, can balance the tree better; that is the idea behind the SOS constraints
some solvers offer (lesson 6.6.2 builds the same effect from binaries: MathOpt's documentation lists
SOS constraints among its model features, but its Python API in OR-Tools 9.15 has no call that adds
one).

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**relaxation.py.** Prints the tiny data, solves the LP relaxation with GLOP and the MILP with HiGHS
(*The Model* and *Dropping Integrality Gives an LP Whose Value Bounds Every Plan From Above*).
*Try:* Raise the budget to 12,320 in a copy of the model. Predict which variables stop being
fractional, then run it.

- Program: [relaxation.py](src/relaxation.py)

**first_branch.py.** Lists the 256 tiny plans, splits the allowed ones on $`x_{P003}`$, and solves
the two children's LPs (*Branching Splits the Problem Into Two Children That Keep Every Integer
Plan* and *Each Child Is the Same LP With One Bound Changed*). *Try:* Split on $`x_{P001}`$
instead. Predict how many allowed plans land in each child.

- Program: [first_branch.py](src/first_branch.py)

**crew_branch.py.** The two-crew example branched on floor and ceiling until every leaf is
integral or infeasible (*A General Integer Branches on Floor and Ceiling*). *Try:* Change the tree
crew's value from 8 to 7. Predict the root LP point, then run it.

- Program: [crew_branch.py](src/crew_branch.py)

**full_tree.py.** The whole tiny tree with no pruning by bound (*Branching Stops at a Node Whose LP
Is Infeasible or Integral*). *Try:* Count the nodes below node 2. Predict how many of them could
hold a plan worth more than 3,054.7.

- Program: [full_tree.py](src/full_tree.py)

**selection.py.** The selection model for any portfolio, `solve_lp` for one node, and a quiet
HiGHS solve. It prints nothing.

- Library: [selection.py](src/selection.py)

**bnb.py.** The LP-based branch-and-bound with every rule of this module as a switch, and `show`,
which prints a tree. It prints nothing.

- Library: [bnb.py](src/bnb.py)
