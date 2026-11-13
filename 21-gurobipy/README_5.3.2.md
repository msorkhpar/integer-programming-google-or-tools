# 5.3.2 Duals, Reduced Costs and Sensitivity Attributes

GridCap's finance partner has read lesson 2.3.4 and asks the modeling team three questions about
next year's capital plan: what one more $k of the 2030 budget is worth, up to how much extra the
answer holds, and how much a deferred project's NPV would have to rise before the plan takes it. In
lesson 4.2.2 MathOpt answered the first with `dual_values`; MathOpt has no call for the other two,
and lesson 2.3.3 got them from HiGHS's own interface. Gurobi answers all three with attributes of the
solved model. This lesson reads them on the LP relaxation of GridCap small's selection model, checks
each against a re-solve, and shows what Gurobi offers, and refuses, for a MIP. GridCap is a
fictional utility, and its numbers are teaching data.

The words come from lessons 2.3.1–2.3.3: a row's **dual value** (or shadow price) is how much the
optimal objective changes per unit of extra right-hand side; a variable's **reduced cost** is how
much the objective changes per unit the variable is pushed away from the bound it sits at; and
**ranging** gives the interval over which each of those numbers holds. All three are properties of
an optimal **basic** LP solution, the vertex a simplex method ends on (lesson 2.2.2).

## The Model

The selection model of lesson 5.3.1 with its integrality dropped, the **LP relaxation** (lesson
3.1.1): each $`x_i`$ may take any value from 0 to 1.

**Sets.** $`P`$ the candidate projects; $`Y`$ the years 2027–2031; $`M \subseteq P`$ the must-do
projects; $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, with parent
$`p(c)`$.

**Parameters.** $`v_i`$, project $`i`$'s NPV at its earliest start ($k); $`c_{i,y}`$, its spend in
year $`y`$ at that start ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`0 \le x_i \le 1`$ for every $`i \in P`$ (the MIP of the last section has
$`x_i \in \{0, 1\}`$).

**Objective.** $`\max \sum_{i \in P} v_i\, x_i`$.

**Constraints.**

```math
\begin{aligned}
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(needs}_c) \\
\sum_{i \in P} c_{i,y}\, x_i &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

`build_selection(env, small, integer=False)` builds it; the rows are named as in lesson 5.3.1
(`budget[2030]`, `alt_G001`, …). The first sections use a smaller LP, stated where it appears.

## An Optimal LP Carries Pi, RC, Slack and a Basis

The LP of OR-Tools' `advanced_linear_programming.py` sample, which lesson 4.2.2 solved with GLOP
through MathOpt: three variables $`x_0, x_1, x_2 \ge 0`$,

```math
\begin{aligned}
\max\;& 10 x_0 + 6 x_1 + 4 x_2 \\
\text{s.t.}\;& 10 x_0 + 4 x_1 + 5 x_2 \le 600 && \text{(c1)} \\
& 2 x_0 + 2 x_1 + 6 x_2 \le 300 && \text{(c2)} \\
& x_0 + x_1 + x_2 \le 100 && \text{(c3)}
\end{aligned}
```

In gurobipy, with every LP result read as an attribute:

```python
rows, cols = [c1, c2, c3], [x[0], x[1], x[2]]
print("status     :", STATUS[m.Status], "| objective", round(m.ObjVal, 4))
print("X          :", [round(v, 4) for v in m.getAttr("X", cols)])
print("Pi         :", [round(p, 4) + 0.0 for p in m.getAttr("Pi", rows)])
print("Slack      :", [round(s, 4) + 0.0 for s in m.getAttr("Slack", rows)])
print("RC         :", [round(r, 4) + 0.0 for r in m.getAttr("RC", cols)])
print("CBasis     :", m.getAttr("CBasis", rows), "(0 basic, -1 nonbasic)")
print("VBasis     :", m.getAttr("VBasis", cols), "(0 basic, -1 at lower bound, -2 at upper bound)")
```

```text
status     : OPTIMAL | objective 733.3333
X          : [33.3333, 66.6667, 0.0]
Pi         : [0.6667, 0.0, 3.3333]
Slack      : [0.0, 100.0, 0.0]
RC         : [0.0, 0.0, -2.6667]
CBasis     : [-1, 0, -1] (0 basic, -1 nonbasic)
VBasis     : [0, 0, -1] (0 basic, -1 at lower bound, -2 at upper bound)
```

The numbers are the ones GLOP returned in lesson 4.2.2, under Gurobi's names:

| MathOpt | gurobipy attribute | Of | Here |
| --- | --- | --- | --- |
| `dual_values(rows)` | `Pi` | row | c1 is worth 0.6667 per unit, c3 3.3333, c2 0 |
| `reduced_costs(vars)` | `RC` | variable | $`x_2`$ would cost 2.6667 per unit forced in |
| `constraint_status(rows)` | `CBasis` | row | c2 is basic (it has slack, 100), c1 and c3 are not |
| `variable_status(vars)` | `VBasis` | variable | $`x_0`$, $`x_1`$ basic; $`x_2`$ at its lower bound 0 |
| (none; compute it) | `Slack` | row | $`\text{RHS} - a^\top x`$: c2 has 100 left |

The basis codes are numbers: a row's `CBasis` is 0 if the row is basic (its slack is in the basis)
and $`-1`$ if not; a variable's `VBasis` is 0 if basic, $`-1`$ at its lower bound, $`-2`$ at its
upper bound, and $`-3`$ superbasic (nonbasic yet strictly between its bounds). Complementary slackness (lesson 2.3.2) is visible: the row with slack,
c2, has price 0, and the two tight rows have prices.

These attributes exist only when they make sense. The attribute reference says `Pi` and `RC` are
available for **continuous, convex** models, and `CBasis`, `VBasis` and every `SA` range below only
for **basic** solutions. Reading one that is not there raises an error, as the last section shows.

## The Sign of Pi Follows the Model's Sense

The same LP can be written as a minimization of $`-f`$. The plan cannot change, but the prices
change sign:

```python
m.setObjective(-(10 * x[0] + 6 * x[1] + 4 * x[2]), GRB.MINIMIZE)
m.optimize()
print("minimize -f:", round(m.ObjVal, 4), "| Pi", [round(p, 4) + 0.0 for p in m.getAttr("Pi", rows)],
      "| RC", [round(r, 4) + 0.0 for r in m.getAttr("RC", cols)])
```

```text
minimize -f: -733.3333 | Pi [-0.6667, 0.0, -3.3333] | RC [0.0, 0.0, 2.6667]
```

Both are right. `Pi` is the rate of change of the objective *as written*: one more unit of c1 raises
$`f`$ by 0.6667, so it lowers $`-f`$ by 0.6667. The linear constraint attribute page states the
rule:

| Sense of the model | $`\le`$ row | $`\ge`$ row | $`=`$ row |
| --- | --- | --- | --- |
| minimize | $`\pi \le 0`$ | $`\pi \ge 0`$ | any sign |
| maximize | $`\pi \ge 0`$ | $`\pi \le 0`$ | any sign |

So before quoting a price to finance, check the sense: for GridCap's maximized NPV, a budget row's
`Pi` is the NPV gained per extra $k, and it is never negative.

A variable's reduced cost follows from the prices. For a column $`j`$ with objective coefficient
$`c_j`$ and coefficients $`a_{ij}`$ in the rows,

```math
\text{RC}_j \;=\; c_j - \sum_{i} a_{ij}\, \pi_i
```

the value the variable brings, less what the rows it uses charge at their prices. For $`x_2`$:
$`4 - (5 \times 0.6667 + 6 \times 0 + 1 \times 3.3333) = -2.6667`$. In a maximization at optimum, a
variable at its lower bound has $`\text{RC} \le 0`$ (bringing it in would not pay) and one at its
upper bound $`\text{RC} \ge 0`$; a basic variable has $`\text{RC} = 0`$.

<!-- practice 1 -->

## A Price Holds Only Inside SARHSLow to SARHSUp

On GridCap small's LP relaxation, `Pi` gives each year's budget price, and two more row attributes
give its range: **`SARHSLow`** and **`SARHSUp`**, the lowest and highest right-hand side for which
the current optimal basis stays optimal. Inside that interval the price is constant and the
objective changes by exactly $`\pi \times \Delta`$:

```python
sel = build_selection(env, small, integer=False)          # 0 <= x_i <= 1: the LP relaxation
m = sel.model
m.optimize()
base = m.ObjVal
print("LP relaxation:", STATUS[m.Status], round(base, 2))
print("row           Pi      RHS   SARHSLow  SARHSUp")
for y, row in sel.budget.items():
    print(f"{row.ConstrName:13} {row.Pi:6.4f} {row.RHS:7,.0f} {row.SARHSLow:9,.1f} {row.SARHSUp:9,.1f}")
```

```text
LP relaxation: OPTIMAL 23669.49
row           Pi      RHS   SARHSLow  SARHSUp
budget[2027]  0.6475   8,890   7,824.2  13,504.2
budget[2028]  0.5765   8,120   7,500.0   8,350.0
budget[2029]  0.0000   8,760   8,070.0       inf
budget[2030]  1.3817   8,610   7,620.0   9,300.0
budget[2031]  0.0000   7,850   5,030.0       inf
```

The objective, 23,669.49, and the prices are the ones GLOP gave through MathOpt in lesson 4.2.2
(0.6475, 0.5765, 0, 1.3817, 0), and the module's tests check every price against GLOP's. The new
columns answer finance's second question. One more $k in 2030 is worth $1.38k of NPV, and that holds
from a 2030 budget of 7,620 up to 9,300. 2029 and 2031 have money to spare, so their price is 0, and
no amount of extra budget changes that (the upper end is infinite); cutting them too far would
(below 8,070 and 5,030).

The program checks the 2030 range by re-solving, once inside it, once at its end and once past it:

```python
row = sel.budget[2030]
pi, rhs, up = row.Pi, row.RHS, row.SARHSUp
for new in (rhs + 100, up, up + 300):
    row.RHS = new
    m.optimize()
    print(f"budget 2030 = {new:8,.1f}: objective {m.ObjVal:9,.2f}  gain {m.ObjVal - base:7,.2f}"
          f"  Pi x change {pi * (new - rhs):7,.2f}")
row.RHS = rhs
m.optimize()
```

```text
budget 2030 =  8,710.0: objective 23,807.66  gain  138.17  Pi x change  138.17
budget 2030 =  9,300.0: objective 24,622.85  gain  953.35  Pi x change  953.35
budget 2030 =  9,600.0: objective 25,001.41  gain 1,331.92  Pi x change 1,367.86
```

Up to 9,300 the gain is the price times the change, to the cent. Past it, the 300 extra $k earn
$`1{,}331.92 - 953.35 = 378.57`$, about 1.26 per $k instead of 1.38: the basis changed, and with it
the price. That is the answer finance needs: "about $1.38k per extra $k, for up to $690k more"
($`9{,}300 - 8{,}610`$), and a new solve beyond that. Two limits from lesson 2.3.3 still apply: a
range assumes **one change at a time** (moving two budgets together can cross a breakpoint neither
crosses alone), and it describes the **LP relaxation**, not the yes/no plan (lesson 2.3.4 and the
last section).

<!-- practice 2 -->

## Objective Ranging Says How Far a Project's NPV Can Move

The third question, how much a project's NPV must change before the plan changes, is answered by
two variable attributes: **`SAObjLow`** and **`SAObjUp`**, the range of the objective coefficient
over which the current basis stays optimal. Read next to `X`, `VBasis` and `RC`:

```python
print("var        X  VBasis       RC     Obj  SAObjLow   SAObjUp")
for pid in ("P005", "P002", "P024", "P001"):
    v = sel.x[pid]
    print(f"{v.VarName:8} {v.X:5.3f} {v.VBasis:4} {v.RC + 0.0:10.2f} {v.Obj:7,.0f} {v.SAObjLow + 0.0:9,.1f} {v.SAObjUp:9,.1f}")
```

```text
var        X  VBasis       RC     Obj  SAObjLow   SAObjUp
x[P005]  1.000   -2     576.00     576       0.0       inf
x[P002]  0.000   -1    -551.93     386      -inf     937.9
x[P024]  0.729    0       0.00     490     388.2     522.2
x[P001]  1.000    0       0.00   1,401     849.1       inf
```

Four cases, one per row:

- **P005 is at its upper bound** ($`-2`$), fully funded. Its NPV could fall to 0 and the LP would
  still fund it, and any rise only confirms it. Its reduced cost equals its NPV, 576: P005 spends
  $1,510k only in 2029, whose price is 0, so the rows charge it nothing.
- **P002 is at its lower bound** ($`-1`$), deferred. Its NPV of 386 would have to exceed 937.9
  before the LP funds any of it, and the gap, $`937.9 - 386 = 551.9`$, is its reduced cost with the
  sign dropped. That is the "why deferred" number lesson 9.3.2 builds on.
- **P024 is basic and fractional** (0.729): the LP funds 73% of it, and the basis holds while its NPV
  stays between 388.2 and 522.2.
- **P001 is basic at 1.000.** A basic variable can sit at a bound; the LP is then **degenerate**
  (lesson 2.2.3), and its range, 849.1 upward, is for this basis.

Where does P002's reduced cost come from? Its column has two nonzero coefficients, and the program
prints what each row charges at its price:

```python
v = sel.x["P002"]
column = m.getCol(v)
terms = [(column.getConstr(k).ConstrName, column.getCoeff(k), column.getConstr(k).Pi) for k in range(column.size())]
print(f"{v.VarName}'s column:")
for name, a, price in terms:
    print(f"  {name:12} a {a:6,.0f}  Pi {price:8.4f}  charge {a * price:9.2f}")
```

```text
x[P002]'s column:
  alt_G001     a      1  Pi 640.0588  charge    640.06
  budget[2027] a    460  Pi   0.6475  charge    297.87
  RC = 386 - 937.93 = -551.93  (Gurobi's RC -551.93)
```

`getCol` returns a variable's column: the rows it appears in and its coefficients there. P002 spends
$460k in 2027, charged at 0.6475, and it belongs to alternative group G001, whose single seat the
LP prices at 640.06. The sum, 937.93, is
`SAObjUp`, the NPV P002 would need. The budget alone would have said 297.87; the alternative group
is most of the reason P002 waits.

## A MIP Has No Duals; fixed() Prices the Plan It Found

Now the real model, with $`x_i \in \{0, 1\}`$:

```python
m.optimize()
print("MIP:", STATUS[m.Status], m.ObjVal, "| IsMIP", m.IsMIP)
try:
    print(sel.budget[2027].Pi)
except (AttributeError, gp.GurobiError) as error:
    print("Pi on a MIP:", type(error).__name__, error)
```

```text
MIP: OPTIMAL 22532.0 | IsMIP 1
Pi on a MIP: AttributeError Unable to retrieve attribute 'Pi'
```

A MIP's best value jumps when a budget crosses a project's cost, so there is no rate of change to
report, and Gurobi reports none: `Pi` (and `RC`, `SARHSLow` and the rest) are for continuous models
only. MathOpt said the same with `has_dual_feasible_solution() == False` (lesson 4.2.2).

What Gurobi does offer is **`Model.fixed()`**: a new model, continuous, in which every integer
variable is fixed at its value in the MIP's solution, as the Python reference describes it. Solved,
it is an LP, and it has prices:

```python
f = m.fixed()                                   # a new LP: every binary fixed at its solution value
f.optimize()
print("fixed():", STATUS[f.Status], f.ObjVal, "| IsMIP", f.IsMIP, "| fixed vars",
      sum(1 for v in f.getVars() if v.LB == v.UB))
print("budget Pi in the fixed LP:", [round(f.getConstrByName(f"budget[{y}]").Pi, 4) + 0.0 for y in small.years])
for pid in ("P001", "P002"):
    v = f.getVarByName(f"x[{pid}]")
    print(f"  {v.VarName}: X {v.X + 0.0:g}  LB {v.LB + 0.0:g}  UB {v.UB + 0.0:g}  RC {v.RC:,.1f}")
```

```text
fixed(): OPTIMAL 22532.0 | IsMIP 0 | fixed vars 40
budget Pi in the fixed LP: [0.0, 0.0, 0.0, 0.0, 0.0]
  x[P001]: X 1  LB 1  UB 1  RC 1,401.0
  x[P002]: X 0  LB 0  UB 0  RC 386.0
```

The fixed LP has the MIP's value, 22,532, and duals, but read them carefully. Every budget price is
0: with all 40 variables fixed ($`\text{LB} = \text{UB}`$), no budget can change the plan, so no
budget is worth anything. Each variable's reduced cost is its whole NPV, because the bound, not any
row, holds it in place. In this selection model, where every variable is a binary, the fixed LP
prices only the decisions already taken. Fixed-integer duals mean something when the model also has
continuous variables (spend, carry-over, draws on a credit line) that stay free once the binaries
are fixed; lessons 9.2.1 and 9.2.2 take that up, and say when such prices can be trusted.

## Summary

- **An optimal LP carries Pi, RC, Slack and a basis.** `Pi` and `Slack` on rows, `RC` on variables,
  `CBasis` and `VBasis` for the basis; on the sample LP they match GLOP's values in MathOpt.
- **The sign of Pi follows the model's sense.** In a maximization a $`\le`$ row's price is
  $`\ge 0`$; minimize $`-f`$ and every sign flips. $`\text{RC}_j = c_j - \sum_i a_{ij}\pi_i`$.
- **A price holds only inside SARHSLow to SARHSUp.** GridCap's 2030 budget is worth $1.38k per $k
  from 7,620 to 9,300; a re-solve confirmed the price to the cent inside and found less past it.
- **Objective ranging says how far a project's NPV can move.** `SAObjLow` and `SAObjUp`; a deferred
  project needs `SAObjUp`, here its NPV less its reduced cost, and `getCol` shows which rows set it.
- **A MIP has no duals; `fixed()` prices the plan it found.** `Pi` raises on a MIP. The fixed LP of
  an all-binary model prices the bounds, not the budgets.

## Reference

| Attribute | Of | Meaning | Available |
| --- | --- | --- | --- |
| `Pi` | linear row | dual value (shadow price) | continuous convex models |
| `Slack` | linear row | right-hand side minus the row's value | after a solve |
| `RC` | variable | reduced cost | continuous convex models |
| `CBasis`, `VBasis` | row, variable | basis status: 0 basic, $`-1`$ nonbasic / at lower, $`-2`$ at upper, $`-3`$ superbasic | basic solutions |
| `SARHSLow`, `SARHSUp` | linear row | right-hand-side range of the current basis | basic solutions |
| `SAObjLow`, `SAObjUp` | variable | objective-coefficient range of the current basis | basic solutions |
| `SALBLow`, `SALBUp`, `SAUBLow`, `SAUBUp` | variable | ranges of the lower and upper bound | basic solutions |

| Task | gurobipy |
| --- | --- |
| all prices of a list of rows | `m.getAttr("Pi", rows)` |
| a variable's column | `col = m.getCol(v)`; `col.getConstr(k)`, `col.getCoeff(k)`, `col.size()` |
| a row or a variable by name | `m.getConstrByName("budget[2030]")`, `m.getVarByName("x[P002]")` |
| the LP relaxation of a model | build it with continuous variables, or `m.relax()` |
| the fixed-integer LP | `f = m.fixed(); f.optimize()` |

| Term | Meaning |
| --- | --- |
| basic solution | a vertex of the LP, described by which variables and slacks are in the basis |
| ranging | the interval of one number (a right-hand side, a coefficient) over which the basis stays optimal |
| degenerate | an LP whose optimal vertex has a basic variable at a bound |
| fixed model | the LP left when a MIP's integer variables are fixed at their solution values |

**Further reading.** Gurobi,
[Linear constraint attributes](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/constraintlinear.html)
(`Pi` and its sign rule, `Slack`, `CBasis`, `SARHSLow`, `SARHSUp`),
[Variable attributes](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/variable.html)
(`RC`, `VBasis` and its codes, `SAObjLow`, `SAObjUp`, the bound ranges) and
[Python API: Model](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html)
(`fixed`, `getAttr`, `getCol`). OR-Tools,
[`advanced_linear_programming.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py),
the sample whose LP the first sections port. Gurobi's
[infeasibility and sensitivity examples tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html)
lists a `sensitivity` example among its programs.

## Challenges

1. Read `SALBLow` and `SALBUp` for P024 and say in words what they mean for a planner.
2. Raise the 2028 budget past its `SARHSUp` of 8,350 and predict, before running, whether the gain
   per $k will be above or below 0.5765.
3. Build the timing model of lesson 5.3.1 with continuous variables and read the budget prices.
   Which year is the dearest?

## Design Note: A Price Is a Sentence With a Range in It

Finance does not need `Pi`; it needs "each extra $k of the 2030 budget is worth about $1.38k, for up
to $690k more, if nothing else changes". Every part of that sentence is an attribute: `Pi`,
`SARHSUp − RHS`, and the one-change-at-a-time rule. A report that prints prices without ranges
invites the reading "another $5M is worth $6.9M", which the re-solve here already disproved at
$300k past the range. Lesson 9.3.1 builds a binding-constraints report around exactly this sentence.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Each needs a Gurobi license in the runner
(lesson 5.3.4).

**lp_duals.py.** The sample LP's `Pi`, `Slack`, `RC`, `CBasis` and `VBasis`, then the same LP as a
minimization (*An Optimal LP Carries Pi, RC, Slack and a Basis*, *The Sign of Pi Follows the Model's
Sense*). *Try:* Change c3's right-hand side to 120 and predict which prices change.

- Program: [lp_duals.py](src/lp_duals.py)

**sensitivity.py.** GridCap small's LP relaxation: budget prices and their ranges checked by
re-solving, objective ranges, and P002's reduced cost taken apart (*A Price Holds Only Inside
SARHSLow to SARHSUp*, *Objective Ranging*). *Try:* Check the 2027 range the same way, at its
`SARHSUp` of 13,504.2.

- Program: [sensitivity.py](src/sensitivity.py)

**mip_duals.py.** The MIP's missing `Pi`, and the prices of its fixed LP (*A MIP Has No Duals*).
*Try:* Print the reduced costs of every funded project in the fixed LP, and predict their sum.

- Program: [mip_duals.py](src/mip_duals.py)
