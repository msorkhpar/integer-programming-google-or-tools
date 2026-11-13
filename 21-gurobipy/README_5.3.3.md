# 5.3.3 `computeIIS`, `feasRelax` and `setObjectiveN`

Finance's scenario from lesson 4.3.5 is back: the board promises P032 for 2027, and the 2030 and
2031 budgets are capped at $5,000k each. The model says **INFEASIBLE**. In lesson 4.3.5 MathOpt
could not explain it, because only Gurobi computes an infeasible subsystem through MathOpt and
Gurobi does not load there; the team found the conflict with a hand-written deletion filter. Now
they have gurobipy, and finance has two more questions: if the scenario cannot hold, what is the
smallest change that makes it hold, and, once it does, can the plan put NPV first and spending second?
This lesson answers all three with Gurobi's own tools, `computeIIS`, `feasRelax` and `setObjectiveN`,
and adds a fourth, `addGenConstrPWL`, for the piecewise-linear curves of lesson 6.6.2. GridCap is a
fictional utility, and its numbers are teaching data.

Each tool is checked against the course's MathOpt result for the same question: the deletion filter
(lesson 4.3.5), solving objectives in order (lesson 4.3.2), and the lambda form of a curve (lesson
6.6.2). The module's tests run both sides.

## The Model

The timing model of lesson 5.3.1 (`build_plan`), with the scenario's three changes marked.

**Sets.** $`P`$ the projects; $`Y`$ the years 2027–2031; $`T_i \subseteq Y`$ the start years of
project $`i`$; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, project $`i`$'s spend in its $`k`$-th year
of work ($k); $`B_y`$, the budget ($k), with $`B_{2030} = B_{2031} = 5{,}000`$ in the scenario
$`\leftarrow`$ scenario.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for $`i \in P`$, $`t \in T_i`$, and
$`x_{\text{P032},2027} \ge 1`$, the board's promise, as a lower bound $`\leftarrow`$ scenario.

**Objective.** $`\max \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}`$.

**Constraints**, with $`\text{spend}_y = \sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}`$:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\text{spend}_y &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The code names the rows `once_P001`, `must_P017`, `alt_G001`, `after_P007_2029` and `budget_2030`,
the names of lesson 4.3.5's MathOpt model. The later sections change the objective, and state each
change where they make it.

## computeIIS Names the Rows That Clash

An **irreducible infeasible subsystem** (IIS) is a set of constraints and bounds that cannot all hold,
and from which no member can be dropped without the rest becoming feasible (lesson 4.3.5). In
gurobipy it is one call on an infeasible model, and the answer comes back as attributes:

```python
pl.x["P032", 2027].LB = 1
pl.budget[2030].RHS = 5000
pl.budget[2031].RHS = 5000
m.optimize()
print("solve:", m.Status, STATUS[m.Status])

m.computeIIS()
print("IISMinimal:", m.IISMinimal)
rows = [c for c in m.getConstrs() if c.IISConstr]
bounds = [(v.VarName, side) for v in m.getVars() for side, on in (("lower", v.IISLB), ("upper", v.IISUB)) if on]
print(f"IIS: {len(rows)} rows, {len(bounds)} variable bounds")
for c in rows:
    print(f"   {c.ConstrName}: {c.Sense} {c.RHS:,.0f}")
print("P032's promise (LB of x[P032,2027]) in the IIS:", bool(pl.x["P032", 2027].IISLB))
```

```text
solve: 3 INFEASIBLE
IISMinimal: 1
IIS: 3 rows, 0 variable bounds
   must_P017: = 1
   budget_2030: < 5,000
   budget_2031: < 5,000
P032's promise (LB of x[P032,2027]) in the IIS: False
```

The same three rows the deletion filter found in lesson 4.3.5, and the module's tests check that
the two agree. P017 is a must-do project that can start only in 2030 or 2031 and spends $5,310k in
its start year; both years are capped at $5,000k. The board's promise of P032 is not part of the
conflict.

What `computeIIS` sets, as the Python reference lists them:

| Attribute | Of | 1 means |
| --- | --- | --- |
| `IISConstr` | linear row | the row is in the IIS |
| `IISLB`, `IISUB` | variable | its lower / upper bound is in the IIS |
| `IISGenConstr`, `IISQConstr`, `IISSOS` | general, quadratic, SOS constraint | that constraint is in the IIS |
| `IISMinimal` | model | 1 if the subsystem is irreducible; 0 if the search stopped early |

Three details from the documentation decide how to read the result:

- **An IIS is one explanation, not the smallest one.** A model can hold several conflicts; the
  reference says the IIS found is not necessarily the smallest. Fix one, solve again, and another
  may appear: Gurobi's `workforce2` example repeats IIS-and-remove until the model is feasible.
- **It can stop early.** `TimeLimit` and the other limits apply to `computeIIS`; it then returns the
  smallest infeasible subsystem found so far, and `IISMinimal` is 0. On a MIP the computation "can
  be quite expensive", in the words of the infeasibility page.
- **Binary bounds never take part.** The variable attribute page says so for `IISLB` and `IISUB`.
  The promise here is a lower bound on a binary, so Gurobi could not have named it even if it
  mattered. A rule a planner may need to see in an IIS belongs in a named row
  (`m.addConstr(x == 1, name="promise_P032")`), not in a binary's bound. The `IIS...Force` attributes
  (`IISConstrForce = 1` forces a row in, 0 keeps it out) steer the search when some rules are known
  to be fixed.

The IIS can also be written to a file. `m.write(path)` with the extension `.ilp` writes only the
subsystem, in Gurobi's LP text format:

```python
with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "conflict.ilp")
    m.write(path)
    with open(path) as handle:
        text = handle.read()
for line in text.splitlines():                     # the row lines, cut short; the long sums are elided
    if line and not line.startswith(("   +", " x[")):
        print(line if len(line) <= 72 else line[:72] + " ...")
```

```text
\ Model GridCap small plan_copy
\ LP format - for model browsing. Use MPS format to capture full model d ...
Maximize
 
Subject To
 must_P017: x[P017,2030] + x[P017,2031] = 1
 budget_2030: 1320 x[P001,2029] + 1320 x[P001,2030] + 1510 x[P005,2030]
 budget_2031: 1320 x[P001,2030] + 140 x[P003,2031] + 480 x[P006,2031]
Bounds
Binaries
End
```

The program elides the continuation lines of the two budget sums and the list of binaries; the file
holds them in full, with every variable that appears in the three rows. An `.ilp` file is what to
attach to a ticket: it is small, it is readable, and it holds no row outside the conflict.

<!-- practice 1 -->

<!-- practice 2 -->

## feasRelax Repairs the Model, and the Penalties Decide What Gives

An IIS says *which* rules clash. Finance's second question is *how little* must change. A
**feasibility relaxation** answers it: let some rows or bounds be broken, pay a penalty for each
unit broken, and solve for the plan with the least penalty. Gurobi builds it for you with
`feasRelax` (and a short form, `feasRelaxS`): it adds **artificial variables** that measure each
violation, replaces the objective by their weighted total, and `optimize()` then finds the cheapest
repair. Lesson 9.1.4 writes such elastic rows by hand; here Gurobi writes them.

The infeasibility page states two rules first. **`feasRelax` changes the model it is called on**, so
each case below builds the scenario afresh (`scenario()`, the timing model with the scenario's three
changes) and relaxes a copy of it, `pl.model.copy()`: no relaxation is stacked on an earlier one. And **the cost of a repair
is yours to define**, in three parts:

| Argument | Meaning |
| --- | --- |
| `relaxobjtype` | 0: minimize the weighted sum of violations; 1: the weighted sum of their squares; 2: the weighted number of rows and bounds violated |
| `minrelax` | `False`: the result is the least-violation plan; `True`: among least-violation plans, the best for the original objective |
| what may give, at what price | `feasRelaxS(type, minrelax, vrelax, crelax)`: every bound (`vrelax`) and/or every row (`crelax`) at penalty 1; `feasRelax(type, minrelax, vars, lbpen, ubpen, constrs, rhspen)`: only the listed variables and rows, each with its own penalty |

First, every row may give, at 1 per unit:

```python
def scenario():
    pl = build_plan(env, small)
    pl.x["P032", 2027].LB = 1
    pl.budget[2030].RHS = 5000
    pl.budget[2031].RHS = 5000
    pl.model.update()
    return pl


pl = scenario()
relaxed = pl.model.copy()                       # feasRelax changes the model it is called on
relaxed.feasRelaxS(0, False, False, True)       # relaxobjtype 0: sum of violations; rows only
relaxed.optimize()
print("all rows, unit penalty :", STATUS[relaxed.Status], "| violation", relaxed.ObjVal, "|", changes(relaxed))
```

```text
all rows, unit penalty : OPTIMAL | violation 1.0 | ['ArtP_must_P017 = 1']
```

`changes` lists the artificial variables that took a value. The cheapest repair is to break
`must_P017` by 1: do not fund the must-do project. One unit of violation on a row measured in
"projects" is cheaper than 310 units on a row measured in $k, so with equal penalties the
relaxation drops the rule a regulator imposed. That is the arithmetic of unit penalties, not advice.
The penalties must say what may give.

Finance's answer is that budgets may move and the must-do rule may not. So only the budget rows are
offered, at 1 per $k:

```python
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.feasRelax(0, False, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("budget rows only       :", STATUS[relaxed.Status], "| violation", relaxed.ObjVal, "|", changes(relaxed))
```

```text
budget rows only       : OPTIMAL | violation 310.0 | ['ArtN_budget_2030 = 310']
```

The smallest budget repair is $310k more in 2030, exactly P017's $5,310k less the $5,000k cap. The
names follow a pattern the
infeasibility page documents: **`ArtP_<row>`** and **`ArtN_<row>`** are a row's positive and negative
artificial variables, **`ArtL_<var>`** and **`ArtU_<var>`** a variable's lower- and upper-bound
violations. Each enters its row with coefficient $`+1`$ or $`-1`$. The same program reads the
`budget_2030` row of that relaxed copy:

```python
row = relaxed.getRow(relaxed.getConstrByName("budget_2030"))
print("budget_2030 now has    :", [(row.getVar(k).VarName, row.getCoeff(k)) for k in range(row.size())
                                   if row.getVar(k).VarName.startswith("Art")])
```

```text
budget_2030 now has    : [('ArtN_budget_2030', -1.0)]
```

So the relaxed row reads $`\text{spend}_{2030} - \text{ArtN} \le 5{,}000`$: `ArtN` is how far spend
may run over the cap, and `ArtP_must_P017 = 1` above read $`\sum_t x_{\text{P017},t} + \text{ArtP} = 1`$,
P017 left out. A $`\le`$ row is offered only the variable that loosens it.

Counting instead of measuring (`relaxobjtype = 2`) asks a different question, "how few rules must
give?":

```python
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.feasRelax(2, False, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("budget rows, count     :", STATUS[relaxed.Status], "| rows relaxed", relaxed.ObjVal, "|", changes(relaxed))
```

```text
budget rows, count     : OPTIMAL | rows relaxed 1.0 | ['ArtN_budget_2031 = 1,000,000', 'ArtNB_budget_2031 = 1']
```

One row gives, as before, but by **1,000,000**: once a row is counted as broken, how far it breaks
costs nothing more, so any violation is as good as any other and the number Gurobi returned means
nothing. The count works through a binary per offered row, `ArtNB_budget_2031` here, which is 1 for
the row that gives. A count is the right measure for "how many caps must finance lift", never for
"by how much".

Last, `minrelax=True`: among the repairs of least violation, the plan with the best NPV. The call
then optimizes at once, in two phases, and returns the least violation:

```python
pl = scenario()
relaxed = pl.model.copy()
budgets = [relaxed.getConstrByName(f"budget_{y}") for y in small.years]
relaxed.Params.MIPGap = 0.0
phase1 = relaxed.feasRelax(0, True, None, None, None, budgets, [1.0] * len(budgets))
relaxed.optimize()
print("minrelax=True          : least violation", phase1, "| NPV", relaxed.ObjVal, "|", changes(relaxed))
print("rows feasRelax added   :", [c.ConstrName for c in relaxed.getConstrs() if c.ConstrName.startswith(("feas", "CArt"))])
```

```text
minrelax=True          : least violation 310.0 | NPV 19249.0 | ['ArtN_budget_2030 = 310']
rows feasRelax added   : ['feasobj']
```

Phase 1 found the least violation, 310; phase 2 added the row `feasobj`, holding the violation at
that value, and restored the NPV objective. With $310k more in 2030, the best plan is worth $19,249k.
That is the full answer finance asked for: the cheapest budget change that makes the scenario hold,
and what the plan is worth after it.

<!-- practice 3 -->

## setObjectiveN Solves Objectives by Priority, Highest First

Lesson 4.3.2 asked the scenario-free model for the most NPV first, then the least total spend among
those plans, and solved it in order by hand, because no solver in the runner takes MathOpt's
auxiliary objectives. Gurobi takes several objectives natively. The model is the timing model with
two objectives in place of one:

```math
\begin{aligned}
&\text{first:} && \max \; f_0(x) = \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t} \\
&\text{then:} && \min \; f_1(x) = \sum_{y \in Y} \text{spend}_y \quad \text{over the plans with } f_0(x) \ge (1 - \varepsilon)\, f_0^*
\end{aligned}
```

with $`f_0^*`$ the best NPV and $`\varepsilon`$ the share of it the plan may give up. In gurobipy:

```python
m.ModelSense = GRB.MAXIMIZE                          # one sense for every objective
total_spend = gp.quicksum(pl.spend.values())
m.setObjectiveN(pl.npv, index=0, priority=npv_priority, weight=1.0, reltol=npv_reltol, name="npv")
m.setObjectiveN(total_spend, index=1, priority=spend_priority, weight=-1.0, name="spend")  # -1: minimize
m.Params.MIPGap = 0.0
m.optimize()
values = []
for k in range(m.NumObj):
    m.Params.ObjNumber = k                           # which objective ObjNVal reads
    values.append(m.ObjNVal)
```

```text
NPV, then spend, exact       OPTIMAL  NPV    24,260  spend    41,630  projects 27
NPV within 1%, then spend    OPTIMAL  NPV    24,031  spend    40,440  projects 26
spend first, then NPV        OPTIMAL  NPV     2,684  spend     7,630  projects 4
```

The three rows are lesson 4.3.2's, to the dollar: exact, 24,260 of NPV for 41,630 of spend; with 1%
of NPV allowed to go, 24,031 for 40,440; spend first, the four must-do projects alone. The module's
tests compare Gurobi's spend under the 1% tolerance with lesson 4.3.2's solve in order. Four rules
from the multiple-objectives page make the code read right:

- **Higher priority goes first.** `priority=2` beats `priority=1`. MathOpt is the other way round:
  its *lowest* priority number goes first (lesson 4.3.2). Porting a model between the two means
  reversing the order.
- **One sense for all.** `ModelSense` applies to every objective, so a minimized objective in a
  maximized model gets `weight=-1.0`. `ObjNVal` still reports the objective as written: spend is
  printed as 41,630, not $`-41{,}630`$.
- **Tolerances belong to the earlier objective.** `reltol` and `abstol` on objective 0 say how far
  it may degrade while later ones are optimized; the looser of the two applies. For a MIP the page
  measures that from a base that includes the MIP gap of the earlier pass, which is why the program
  sets `MIPGap = 0`: with the default gap, "exact" would already allow a little loss.
- **Equal priorities blend.** Objectives with the same priority are summed with their weights in one
  pass; distinct priorities are solved one after another. Each objective is read with
  `Params.ObjNumber = k` then `ObjNVal`.

The page also lists what a multi-objective model gives up: no duals or basis (`Pi`, `RC`, `VBasis`,
`CBasis`), and no `ObjBound` or `MIPGap` for the whole solve. Every objective must be linear.

## addGenConstrPWL States y = f(x) in One Row

Lessons 6.6.1 to 6.6.3 wrote piecewise-linear curves by hand, because MathOpt's Python model has no SOS2
constraint: the lambda form of lesson 6.6.2 needed a weight per breakpoint and a binary per segment.
gurobipy has a **general constraint** for it, `addGenConstrPWL(x, y, xpts, ypts)`: the point
$`(x, y)`$ must lie on the curve through the breakpoints $`(x_j, y_j)`$, and Gurobi builds the
formulation itself.

The model is lesson 6.6.2's: the one-period selection model on GridCap small, with a falling-tier
credit line. Its new parts are a draw $`0 \le d \le 5{,}000`$ ($k) and its cost $`\kappa \ge 0`$
($k), tied by the curve $`f`$ through (0, 0), (1,500, 675), (3,000, 1,050), (5,000, 1,250):

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{npv}_i\, x_i - \kappa \\
\text{s.t.}\;& \kappa = f(d) && && \text{(credit)} \\
& \sum_{i \in P} \text{capex}_i\, x_i \le B + d && && \text{(budget)} \\
& x_i = 1 \;\; \forall i \in M, \quad x_c \le x_{p(c)} \;\; \forall c \in C, \quad \textstyle\sum_{i \in g} x_i \le 1 \;\; \forall g \in \mathcal{G} && && \text{(must, parent, alt)} \\
& x_i \in \{0, 1\}, \quad 0 \le d \le 5{,}000, \quad \kappa \ge 0
\end{aligned}
```

with $`B = 38{,}390`$, GridCap small's capital budget. Lesson 6.6.2 is in section 6, which the course
reaches later, and this section does not need it: the model is the one above. "Lesson 6.6.2's
optimum" below means the lines that lesson recorded when it solved this model in MathOpt, with a
weight per breakpoint and a binary per segment:

<!-- unverified -->
```text
weights + seg binaries: objective $26,753k, drawn $4,900k, weights [0.0, 0.0, 0.05, 0.95]
                        cost charged $1,240k, real cost $1,240k, plan really worth $26,753k
                        segment binaries [0, 0, 1]
```

The curve is one call:

```python
draw = m.addVar(lb=0, ub=XS[-1], name="draw")               # $k drawn from the credit line
cost = m.addVar(lb=0, name="cost")                          # what the draw costs, $k
m.addGenConstrPWL(draw, cost, XS, YS, name="credit")        # cost = f(draw), f through the breakpoints
m.addConstr(gp.quicksum(p.capex * x[p.project_id] for p in small.projects) <= small.capital_budget + draw,
            name="budget")
```

```text
OPTIMAL: objective $26,753k, drawn $4,900k, cost $1,240k
general constraints: 1 | variables: 42 | binaries: 40
```

$26,753k with a $4,900k draw costing $1,240k: lesson 6.6.2's optimum, which its lambda form with
segment binaries reached. The model holds 42 variables, the 40 projects plus the draw and its cost,
and one general constraint; the weights and segment binaries of lesson 6.6.2 are Gurobi's business
now. The constraints page says each such general constraint has an equivalent MIP formulation and
that adding one to a continuous model makes it a MIP.

Two rules for the breakpoints, from the objectives page, which defines the piecewise-linear
function both features share: the $`x`$ values must not decrease (a repeated $`x`$ makes a jump),
and **outside the first and last breakpoints the curve goes on**, along the first and last pieces:

```python
for at in (-1000, 6000):
    u.LB = u.UB = at
    probe.optimize()
    print(f"f({at:,}) = {v.X:,.0f}")
```

```text
f(-1,000) = -450
f(6,000) = 1,350
```

The first piece has slope $`675 / 1{,}500 = 0.45`$, so $`f(-1{,}000) = -450`$; the last has slope
$`200 / 2{,}000 = 0.1`$, so $`f(6{,}000) = 1{,}250 + 100 = 1{,}350`$. A credit line does not lend
past $5,000k at 10 cents on the dollar, so the curve's domain must be enforced by the variable's
bounds: `draw` has `ub=XS[-1]`. Leave the bound off and the model may draw more on terms the offer
never made.

## Summary

- **computeIIS names the rows that clash.** `IISConstr`, `IISLB`, `IISUB` mark the subsystem;
  `IISMinimal` says whether it is irreducible; `.ilp` writes only the conflict. Gurobi named
  `must_P017` and the two caps, as the deletion filter did; binary bounds never take part.
- **feasRelax repairs the model, and the penalties decide what gives.** On a copy: unit penalties on
  every row dropped the must-do project; budget rows only gave $310k more in 2030; counting gave one
  row broken by an arbitrary amount; `minrelax=True` gave the best NPV, $19,249k, at least violation.
- **setObjectiveN solves objectives by priority, highest first.** One sense for the model, weight
  $`-1`$ to minimize, `reltol` on the earlier objective; the results match lesson 4.3.2's.
- **addGenConstrPWL states y = f(x) in one row.** The credit line reached lesson 6.6.2's $26,753k;
  the curve extends past its ends, so bound the variable.

## Reference

| Task | gurobipy |
| --- | --- |
| an IIS | `m.computeIIS()`; then `c.IISConstr`, `v.IISLB`, `v.IISUB`, `m.IISMinimal` |
| write it | `m.write("conflict.ilp")` |
| steer it | `c.IISConstrForce = 1` (in), `0` (out), `-1` (let Gurobi decide) |
| relax everything at unit penalty | `r = m.copy(); r.feasRelaxS(type, minrelax, vrelax, crelax); r.optimize()` |
| relax chosen rows and bounds | `r.feasRelax(type, minrelax, vars, lbpen, ubpen, constrs, rhspen)` |
| several objectives | `m.ModelSense = GRB.MAXIMIZE`; `m.setObjectiveN(expr, index, priority, weight, abstol, reltol, name)` |
| read objective $`k`$ | `m.Params.ObjNumber = k; m.ObjNVal` |
| a piecewise-linear curve | `m.addGenConstrPWL(x, y, xpts, ypts, name)` |

| `feasRelax` name | Meaning |
| --- | --- |
| `ArtP_<row>`, `ArtN_<row>` | the row's violation variables, entering it with $`+1`$ and $`-1`$ |
| `ArtL_<var>`, `ArtU_<var>` | violation of a variable's lower or upper bound |
| `ArtPB_`, `ArtNB_`, `ArtLB_`, `ArtUB_` | binaries that count violations (`relaxobjtype = 2`) |
| `feasobj` | the row `minrelax=True` adds to hold the least violation |

| Term | Meaning |
| --- | --- |
| IIS | a set of rows and bounds that cannot all hold, each one needed for the conflict |
| feasibility relaxation | the model with violations allowed at a price, solved for the cheapest repair |
| hierarchical objectives | objectives solved one after another by priority, each kept within its tolerance |
| general constraint | a constraint of a named kind (max, min, abs, and, or, indicator, piecewise-linear) that Gurobi turns into rows itself |

**Further reading.** Gurobi,
[Infeasibility](https://docs.gurobi.com/projects/optimizer/en/current/features/infeasibility.html)
(IIS and feasibility relaxation, the three cost measures, `minrelax`'s two phases, the names of the
artificial variables),
[Python API: Model](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html)
(`computeIIS`, `feasRelax`, `feasRelaxS`, `copy`, `addGenConstrPWL`),
[Variable attributes](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/variable.html)
and
[Linear constraint attributes](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/constraintlinear.html)
(the `IIS` attributes),
[Multiple objectives](https://docs.gurobi.com/projects/optimizer/en/current/features/multiobjective.html)
(priorities, weights, tolerances, what is not available),
[Constraints](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html)
(general constraints) and
[Objectives](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/objectives.html)
(the piecewise-linear function, its breakpoints and its extension past the ends). Gurobi's
[infeasibility examples tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html)
(`workforce1` to `workforce3` and `feasopt`: IIS, IIS-and-remove, and relaxation).

## Challenges

1. Write the promise as a row, `promise_P032: x[P032,2027] = 1`, and lower the 2027 budget to
   5,000. Does the IIS now name the promise?
2. Offer both the budget rows and `must_P017` to `feasRelax`, the must-do at a penalty of 1,000.
   Predict which gives.
3. Give the NPV objective `abstol=100` instead of `reltol=0.01` and predict the spend.

## Design Note: Penalties Are Policy

Every `feasRelax` call above answered a different question, and each answer was correct: drop a
must-do, add $310k, lift one cap by any amount. The solver does not know which rules are law and
which are wishes; the penalties tell it. A service that offers "make it feasible" (lesson 9.1.6)
keeps those penalties in configuration, reviewed with planners, and reports the repair together
with the penalties that chose it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change. Each needs a Gurobi license in the runner
(lesson 5.3.4).

**iis.py.** The scenario, `computeIIS`, the IIS attributes and the `.ilp` file (*computeIIS Names
the Rows That Clash*). *Try:* Cap only 2030 at 5,000 and predict the IIS before running.

- Program: [iis.py](src/iis.py)

**feas_relax.py.** Four relaxations of the scenario, each on a copy (*feasRelax Repairs the
Model*). *Try:* Give the 2031 row a penalty of 2 and predict which year's budget is raised.

- Program: [feas_relax.py](src/feas_relax.py)

**multi_objective.py.** NPV then spend with `setObjectiveN`, three ways (*setObjectiveN Solves
Objectives by Priority*). *Try:* Give both objectives priority 1 and predict what the blend
maximizes.

- Program: [multi_objective.py](src/multi_objective.py)

**pwl.py.** The credit line with `addGenConstrPWL`, and the curve past its ends (*addGenConstrPWL
States y = f(x) in One Row*). *Try:* Remove the draw's upper bound and predict the draw.

- Program: [pwl.py](src/pwl.py)
