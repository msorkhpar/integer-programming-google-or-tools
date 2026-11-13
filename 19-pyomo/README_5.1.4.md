# 5.1.4 Piecewise Functions and the IIS Tools

Two requests reach the Pyomo model this week. First, GridCap's transmission projects on the small
portfolio need more crew-months than GridCap's own crews have, and the rest must be bought from a
contractor whose price per month rises by tier, so the cost of the shortfall is a piecewise-linear
function. Second, the planners are testing deep cuts to the 2030 and 2031 budgets, and some of the
scenarios come back infeasible; they want to know which rules conflict. This lesson covers Pyomo's
tools for both: its piecewise components, and its tools for explaining an infeasible model,
alongside MathOpt's `compute_infeasible_subsystem` of lesson 4.3.5. Section 6, later in the course,
writes piecewise curves by hand in MathOpt (lessons 6.6.1 to 6.6.3) and checks them against Pyomo's
`Piecewise` (lesson 6.6.4); this lesson does not need them, and says what each idea it borrows
from them means where it uses it. GridCap and its contractor are fictional.

## The Model

The **contractor model** (`contractor_model.py`), a one-period selection on GridCap small:

**Sets.** $`P`$ the projects; $`T \subseteq P`$ the transmission projects; $`M \subseteq P`$ the
must-do projects; $`k = 0, 1, 2, 3`$ the breakpoints of the price curve.

**Parameters.** $`\text{value}_i`$, project $`i`$'s NPV at its earliest start ($k);
$`\text{capex}_i`$ ($k); $`\text{months}_i`$, the crew-months it needs; $`B = 38{,}390`$, the
capital budget ($k); $`O = 40`$, the crew-months GridCap's own crews cover; the breakpoints
$`(b_k, f_k)`$: $`b = (0, 10, 20, 40)`$ months, and $`f = (0, 300, 750, 2150)`$ ($k) for the rising
tiers ($30k, $45k, $70k a month) or $`f = (0, 450, 750, 1150)`$ for a volume-discount offer ($45k,
$30k, $20k a month). $`f(b)`$ is the curve through them.

**Variables.** $`x_i \in \{0, 1\}`$ for $`i \in P`$; $`0 \le b \le 40`$, contractor crew-months
bought; $`c \ge 0`$, their cost ($k).

**Objective.**

```math
\max \; \sum_{i \in P} \text{value}_i\, x_i - c
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must\_do}_i) \\
\sum_{i \in T} \text{months}_i\, x_i &\le O + b && && \text{(crews)} \\
c &\ge f(b) && && \text{(tiers)}
\end{aligned}
```

| Label | Pyomo |
| --- | --- |
| budget, must_do$`_i`$, crews | `m.budget`, `m.must_do[i]`, `m.crews` |
| tiers | `m.tiers`, a `Piecewise` component |
| $`x_i`$, $`b`$, $`c`$ | `m.x[i]`, `m.bought`, `m.contract` |

The second half of the lesson uses lesson 5.1.1's timing model, with the 2030 and 2031 budgets
changed; it is stated there.

## Piecewise Writes y Below, Above or Equal to f(x), and the Side Must Match the Push

`pyo.Piecewise(y, x, pw_pts=..., f_rule=..., pw_constr_type=..., pw_repn=...)` adds rows that tie
a variable `y` to a piecewise-linear function of a variable `x`. `pw_pts` are the breakpoints in
`x` and `f_rule` the values there (a list, or a function, or a dict of lists for an indexed
`Piecewise`). `pw_constr_type` says which relation the rows state: `"UB"` for $`y \le f(x)`$,
`"LB"` for $`y \ge f(x)`$, `"EQ"` for $`y = f(x)`$. `pw_repn` names the formulation; lessons 6.6.2
and 6.6.3 build `"CC"` (the lambda form), `"INC"` (incremental) and `"LOG"` by hand; the default is `"SOS2"`.

```python
m.tiers = pyo.Piecewise(m.contract, m.bought, pw_pts=MONTHS, f_rule=cost,
                        pw_constr_type=constr_type, pw_repn=repn, force_pw=force_pw)
```

`contractor_tiers.py` builds the model once per setting, with GridCap's crews covering 40
crew-months, and prints what the `Piecewise` component added, the plan's net value, the months
bought, the cost variable, and the curve's true cost at those months:

```text
rising tiers, LB, SOS2 (default)   +0 vars (0 binary), +3 rows    net  24,839.0  bought 21.0  contract   820.0  curve   820.0
rising tiers, LB, SOS2, force_pw   +4 vars (0 binary), +3 rows    NotImplementedError: Highs interface does not support SOS constraints
rising tiers, LB, INC, force_pw    +5 vars (2 binary), +6 rows    net  24,839.0  bought 21.0  contract   820.0  curve   820.0
rising tiers, EQ, INC              +5 vars (2 binary), +6 rows    net  24,839.0  bought 21.0  contract   820.0  curve   820.0
discount, LB, SOS2 (default)       +4 vars (0 binary), +3 rows    NotImplementedError: Highs interface does not support SOS constraints
discount, LB, INC                  +5 vars (2 binary), +6 rows    net  24,917.0  bought 26.0  contract   870.0  curve   870.0
discount, UB, INC                  +0 vars (0 binary), +3 rows    net  25,787.0  bought 40.0  contract     0.0  curve  1150.0
```

Start with the last line. The objective subtracts $`c`$, so it pushes $`c`$ **down**: the model
wants to pay as little as it can. `"UB"` states $`c \le f(b)`$, which puts no floor under $`c`$,
and the solver took the cheapest value the variable's bounds allow, 0, while buying all 40 months,
whose true cost is $1,150k. The net value of $25,787k is not a plan anyone can buy. The other
discount line, `"LB"` ($`c \ge f(b)`$), pays the curve exactly: 26 months for $870k. The rule is
lesson 6.6.1's in Pyomo's words: a cost the objective pushes down needs `"LB"` (or `"EQ"`), a value it
pushes up needs `"UB"` (or `"EQ"`). `"EQ"` is always exact, and costs binaries for every shape.

Pyomo only writes the rows; it does not know which way your objective pushes. Check the cost
variable against the curve, as the `curve` column does: the two agree on every line but the wrong
one.

The `x` variable needs **both bounds, and they should be the breakpoints' range**. The contractor
model declares `m.bought = pyo.Var(bounds=(MONTHS[0], MONTHS[-1]))`, 0 to 40, the first and last
breakpoints. `piecewise_bounds.py` shows what happens otherwise: the rising tiers on a model of
their own, where each contractor month is worth $100k, more than any tier costs, so the objective
buys as many months as it is allowed. `bought` gets three upper bounds, 40, 60 and none:

```python
def months_bought(upper):
    """Build the curve with `bought` bounded by (0, upper), solve, and say what came back."""
    m = pyo.ConcreteModel()
    m.bought = pyo.Var(bounds=(0, upper))                     # contractor crew-months
    m.contract = pyo.Var(bounds=(0, None))                    # their cost, $k
    try:
        m.tiers = pyo.Piecewise(m.contract, m.bought, pw_pts=MONTHS, f_rule=COST,
                                pw_constr_type="LB", pw_repn="INC")
    except ValueError as error:
        return f"ValueError: {str(error).splitlines()[0]}"
    m.gain = pyo.Objective(expr=100 * m.bought - m.contract, sense=pyo.maximize)
    highs().solve(m)
    return f"bought {m.bought.value:g}, contract {m.contract.value:g}"


for upper in (40, 60, None):
    print(f"bought in [0, {upper}]:")
    print("  ", months_bought(upper))
```

```text
bought in [0, 40]:
   bought 40, contract 2150
bought in [0, 60]:
**WARNING: Piecewise 'tiers[None]' feasible region does not include the upper bound of domain variable: bought.ub = 60 > 40. Refer to the Piecewise help documentation for information on how to disable this warning.
   bought 40, contract 2150
bought in [0, None]:
ERROR: Constructing component 'tiers' from data=None failed:
        ValueError: Piecewise 'tiers[None]' found an unbounded variable used
        for the constraint domain: 'bought'. Piecewise component requires the
        domain variable have lower and upper bounds. Refer to the Piecewise
        help documentation for information on how to disable this restriction
   ValueError: Piecewise 'tiers[None]' found an unbounded variable used for the constraint domain: 'bought'. Piecewise component requires the domain variable have lower and upper bounds. Refer to the Piecewise help documentation for information on how to disable this restriction
```

With no upper bound, `Piecewise` refuses to build: it logs an `ERROR` and raises `ValueError`.
With an upper bound of 60, past the last breakpoint, it builds and prints a `WARNING`, and the rows
it wrote hold `bought` to the curve's range: the plan stops at 40 months, although the variable's
own bound allows 60 and the objective gains $100k for every month it buys. The model is
then not the one its declarations say, and the only sign is a warning in the log. So bound `x` to
exactly the first and last breakpoints, or add breakpoints until they cover the bounds the data
needs.

## A Convex Cost Bounded From Below Needs No Binaries

The first line has no binaries and no new variables, only 3 rows. When it builds the component,
Pyomo checks the breakpoints: if the function is convex and the type is `"LB"`, or concave and the
type is `"UB"`, it replaces the piecewise formulation by one row per segment. For the rising tiers
those are the rows it wrote:

```text
tiers.simplified_piecewise_constraint[1]: - contract + 30.0*bought  <=  0
tiers.simplified_piecewise_constraint[2]: - contract + 300 + 45.0*(bought - 10)  <=  0
tiers.simplified_piecewise_constraint[3]: - contract + 750 + 70.0*(bought - 20)  <=  0
```

$`c \ge 30b`$, $`c \ge 300 + 45(b - 10)`$, $`c \ge 750 + 70(b - 20)`$: $`c`$ above every line, lesson
6.6.1's epigraph of a convex cost, which needs no binaries because the minimizer lands on the
highest line by itself. The plan buys 21 months for $820k, the curve's value (10 × 30 + 10 × 45 +
1 × 70). `force_pw=True` turns the check off and keeps the formulation you named: with `"INC"` it
added 5 variables, 2 of them binary, and 6 rows, for the same answer. Leave the check on; it is free
tightness.

The volume discount is concave, and a concave cost pushed down is the case lesson 6.6.1 showed needs
binaries; Pyomo keeps the formulation (`"INC"`: 2 binaries) and the answer is exact.

## SOS2, the Default, Fails With HiGHS as Soon as Pyomo Writes It

`pw_repn="SOS2"` asks the solver to treat the breakpoint weights as a **special ordered set of type
2**: at most two weights nonzero, and they must be neighbours. HiGHS's Pyomo interface has no SOS
constraints and refuses the model:

```text
rising tiers, LB, SOS2, force_pw   +4 vars (0 binary), +3 rows    NotImplementedError: Highs interface does not support SOS constraints
```

The table shows when that happens. The default is SOS2, and on the rising tiers it **worked**
(first line), because Pyomo's convexity check replaced the formulation by plain rows and no SOS
constraint was ever written. With `force_pw=True`, or with the concave discount (the fifth line),
Pyomo writes the SOS2 constraint and HiGHS refuses it. So a model that leaves `pw_repn` at its
default can run for months and then fail the day a curve changes shape. With HiGHS (and with
MathOpt and CP-SAT, which have no SOS2 either), always name a formulation built from binaries, such
as `"INC"`, `"CC"` or `"DCC"`; the module's tests check that those three give the same optimum here,
and lesson 6.6.4 ran `"LOG"` too. Pyomo's documentation lists CBC, SCIP, Gurobi and CPLEX among the
solvers that accept SOS constraints.

<!-- practice 1 -->

## pyomo.contrib.piecewise Separates the Function From Its Formulation

Newer Pyomo versions have a second piecewise API, `pyomo.contrib.piecewise`, built the way GDP is:
you declare the function as a component, use it in ordinary constraints, and choose the formulation
afterwards with a transformation. A `PiecewiseLinearFunction` can be made from a table of points:

```python
m = build(small, 40)
m.tiers.deactivate()                                    # drop the Piecewise component's rows
m.price = PiecewiseLinearFunction(tabular_data=dict(zip(MONTHS, COST)))
m.pay = pyo.Constraint(expr=m.contract >= m.price(m.bought))
for name in transformations:
    pyo.TransformationFactory(name).apply_to(m)
```

Called on a number it evaluates the curve; called on a variable it gives an expression for a
constraint. The transformations include `contrib.piecewise.incremental`,
`contrib.piecewise.disaggregated_logarithmic` and `contrib.piecewise.inner_repn_gdp`, which writes
the function as a GDP disjunction, one disjunct per segment, for lesson 5.1.3's `gdp.hull` or
`gdp.bigm` to finish:

```text
price(15) = 525.0  price(30) = 1450.0
contrib.piecewise.incremental                    2 binaries  net 24,839.0  bought 21.0  contract 820.0
contrib.piecewise.disaggregated_logarithmic      2 binaries  net 24,839.0  bought 21.0  contract 820.0
contrib.piecewise.inner_repn_gdp + gdp.hull      3 binaries  net 24,839.0  bought 21.0  contract 820.0
```

$`f(15) = 300 + 5 \times 45 = 525`$ and $`f(30) = 750 + 10 \times 70 = 1450`$. All three agree with
the `Piecewise` component, but each wrote binaries for a curve that needed none: the newer API, in
these transformations, does not make the convexity check. Choose the API by what you need: the old
`Piecewise` for one-dimensional curves with its free simplification, the new one for functions of
several variables (it triangulates their domain) or when you want the GDP route.

## The MIS Tool Explains an Infeasible Model With Any Solver, on Its LP Relaxation

Now the budget cuts. The model is lesson 5.1.1's timing model on GridCap small, unchanged except
for two numbers: $`B_{2030} = B_{2031} = \text{cap}`$, with cap $4,000k and then $2,600k (from
$8,610k and $7,850k). Three must-do projects work in those years: P017 spends 5,310 in its start year
(2030 or 2031), P010 spends 130 (2030 or 2031) and P003 spends 140 (2031).

An **irreducible infeasible subsystem** (IIS) is a set of rows and bounds that has no solution
together, while every proper subset of it has one (lesson 4.3.5). Pyomo's
`compute_infeasibility_explanation` (in `pyomo.contrib.iis`; its documentation calls the result a
minimal intractable system, MIS) finds one with any solver Pyomo can call, in two phases:

1. **Elastic filter.** It turns every variable bound into a row, adds a slack variable to each row,
   and lets the solver use the slacks. Each feasible solve names rows whose slack was used, a
   "repair option", and those rows join a candidate set.
2. **Deletion filter.** With the slacks gone and only the candidate rows active, it drops each row
   in turn; if the rest is still infeasible the row stays out, if the rest becomes feasible the row
   is part of the conflict and goes back. The rows left are the MIS.

The tool needs a solver that **reports** an infeasible solve in its results rather than raising,
because it solves many infeasible models on purpose. Pyomo's HiGHS interfaces raise by default
(lesson 5.1.2), so the program hands it a small wrapper:

```python
class HighsThatReturns:
    """HiGHS for the MIS tool: it must report an infeasible solve in its results, not raise."""

    def __init__(self):
        self.highs = pyo.SolverFactory("highs")

    def available(self):
        return self.highs.available()

    def solve(self, model, tee=False):
        try:
            return self.highs.solve(model, tee=tee)
        except NoFeasibleSolutionError:
            return self.highs.solve(model, tee=tee, load_solutions=False,
                                    raise_exception_on_nonoptimal_result=False)
```

and the tool writes its findings to a logger, so `explain` captures that text:

```python
compute_infeasibility_explanation(model, HighsThatReturns(), logger=log)
```

The $2,600k cut:

```text
cap 2,600: MIS rows: ['constraint: spend_cap[2030]', 'constraint: spend_cap[2031]', 'constraint: once[P017]', 'constraint: once[P010]']
  plus 43 lower bounds x >= 0, e.g. ['lb of var x[P030,2030]', 'lb of var x[P036,2030]']
  repair options it logged: 46
```

The four rows say it: P017 and P010 must start (`once` is `== 1` for a must-do), and together they
need 5,310 + 130 = 5,440 across 2030 and 2031, more than 2 × 2,600 = 5,200. P003's row is not in
the set, because the conflict holds without it. The 43 lower bounds are there because the tool
treats bounds as rows too: if any project that spends in 2030 or 2031 could start a negative amount,
it would free money, so each $`x \ge 0`$ is part of the conflict. They are true and uninteresting;
read the rows first. Before the MIS, the log listed 46 repair options from the elastic filter.

Now the $4,000k cut:

```text
cap 4,000: infeasible
  MIS tool: Found model GridCap small timing to be feasible!
```

HiGHS says the MILP is infeasible, and the tool says the model is feasible. Both are right about
different models: the tool replaces every variable's domain by the reals (its source sets each
variable's domain to `Reals` when it turns the bounds into rows), so it explains the **LP
relaxation**. With $4,000k in each year, the relaxation can start half of P017 in 2030 and half in
2031 (2,655 each). The MILP cannot: P017 is one project and spends 5,310 in a single year. An
infeasibility that only integrality causes is invisible to this tool, and it says so by raising.

<!-- practice 2 -->

## write_iis Needs CPLEX, Gurobi or Xpress, and Works on the MILP

`write_iis(model, file_name, solver=None)`, also in `pyomo.contrib.iis`, does not search itself: it
hands the model to a commercial solver's persistent interface (CPLEX, Gurobi or Xpress), asks that
solver for an IIS of the MILP, and writes it to a file in LP format:

```python
with tempfile.TemporaryDirectory() as folder:
    try:
        path = quiet(lambda: write_iis(m, os.path.join(folder, "budget_cut.ilp")))
    except RuntimeError as error:
        print("write_iis:", error)
```

In the course runner without a Gurobi license it finds none of the three and raises
`RuntimeError: Could not find a solver to use, supported solvers are ['cplex', 'gurobi', 'xpress']`,
which is what `write_iis_demo.py` prints there. With a Gurobi license mounted into the runner
(lesson 5.3.4 sets one up), the same program prints the rows of the file Gurobi wrote for the
$2,600k cut: `once(P017)`, `spend_cap(2030)` and `spend_cap(2031)`, three rows and no bounds. That
is smaller than the MIS above, and it is the MILP's conflict: P017 alone spends 5,310 in one year,
more than 2,600, so P010 is not needed. (Gurobi's file writes the names with parentheses.)

The two tools answer different questions, and the difference is integrality:

| Tool | Solver | Explains | On the $2,600k cut |
| --- | --- | --- | --- |
| `compute_infeasibility_explanation` | any Pyomo solver, here HiGHS | the LP relaxation | 4 rows and 43 bounds |
| `write_iis` | CPLEX, Gurobi or Xpress | the MILP | 3 rows |
| MathOpt `compute_infeasible_subsystem` (lesson 4.3.5) | Gurobi only, in this runner none | the MILP | |

## find_infeasible_constraints Checks a Plan Without a Solver

A different question: the planners hand you a plan and ask which rules it breaks under the cut.
That needs no solver at all. Fix every variable at the plan's value and evaluate each row;
`pyomo.util.infeasible.find_infeasible_constraints` does the second step, yielding each violated row
with its body's value:

```python
plan = build(small)
highs().solve(plan)
starts = schedule(plan)
m = cut(4000)
for (i, t), v in m.x.items():
    v.fix(1 if starts.get(i) == t else 0)
for row, body, which in find_infeasible_constraints(m):
    print(f"{row.name}: plan spends {body:,.0f} > {pyo.value(row.upper):,.0f}")
```

```text
spend_cap[2030]: plan spends 8,560 > 4,000
spend_cap[2031]: plan spends 7,720 > 4,000
```

The plan that was optimal under the full budgets spends $8,560k in 2030 and $7,720k in 2031; under
the $4,000k cut those two rows break and every other row still holds. Its companion
`log_infeasible_constraints` writes the same findings to a logger instead. This is also how to test
a planner's hand-made plan against the model before arguing about it.

## Summary

- **Piecewise writes y below, above or equal to f(x), and the side must match the push.** `"UB"` on
  a cost the objective pushes down paid $0 for 40 months whose curve cost is $1,150k. Bound `x` to
  the breakpoints: unbounded, `Piecewise` raises; bounded past them, it only warns, and its rows cap `x`.
- **A convex cost bounded from below needs no binaries.** Pyomo checks convexity and writes one row
  per segment; `force_pw=True` turns that off.
- **SOS2, the default, fails with HiGHS as soon as Pyomo writes it.** It ran on a convex curve only
  because no SOS2 was written; name a binary form such as `"INC"`, `"CC"` or `"DCC"`.
- **pyomo.contrib.piecewise separates the function from its formulation.** A
  `PiecewiseLinearFunction` plus a transformation, including a GDP route; no convexity shortcut.
- **The MIS tool explains an infeasible model with any solver, on its LP relaxation.** Four rows and
  43 bounds on the $2,600k cut; on the $4,000k cut, a conflict only integrality causes, it reports
  the model feasible.
- **write_iis needs CPLEX, Gurobi or Xpress, and works on the MILP.** With Gurobi, three rows.
- **find_infeasible_constraints checks a plan without a solver.** Fix the plan, list the rows it
  breaks.

## Reference

| `Piecewise` argument | Values |
| --- | --- |
| `pw_constr_type` | `"UB"` ($`y \le f(x)`$), `"LB"` ($`y \ge f(x)`$), `"EQ"` |
| `pw_repn` | `"SOS2"` (default; refused by HiGHS when written), `"INC"`, `"CC"`, `"DCC"`, `"LOG"`, `"DLOG"`, `"MC"`, `"BIGM_BIN"`, `"BIGM_SOS1"` |
| `force_pw` | `True` keeps the formulation even when convexity would allow plain rows |
| `pw_pts`, `f_rule` | breakpoints; values as a list, a function or a dict of lists |

| Curve pushed | Convex | Concave |
| --- | --- | --- |
| down (a cost minimized) | `"LB"`, no binaries | `"LB"` with a binary formulation |
| up (a value maximized) | `"UB"` with a binary formulation | `"UB"`, no binaries |

| Infeasibility tool | Import | Needs |
| --- | --- | --- |
| `compute_infeasibility_explanation(m, solver, logger=...)` | `pyomo.contrib.iis` | a solver that returns on infeasible solves |
| `write_iis(m, "file.ilp", solver=None)` | `pyomo.contrib.iis` | CPLEX, Gurobi or Xpress |
| `find_infeasible_constraints(m)`, `log_infeasible_constraints(m)` | `pyomo.util.infeasible` | values on the variables |

**Further reading.** Pyomo documentation, [`Piecewise`](https://pyomo.readthedocs.io/en/stable/api/pyomo.core.base.piecewise.Piecewise.html)
(the constraint types, every `pw_repn` and the convexity check that `force_pw` turns off);
[Infeasibility diagnostics](https://pyomo.readthedocs.io/en/stable/explanation/analysis/iis.html)
(`write_iis` and its three solvers; the MIS tool, its repair options and its origin in Chinneck's
infeasibility tutorial); [Special Ordered Sets](https://pyomo.readthedocs.io/en/stable/explanation/modeling/math_programming/sos_constraints.html)
in the modeling components (what SOS1 and SOS2 mean, and which solvers the page lists as accepting
them). The `pyomo.contrib.piecewise` transformation modules are listed in the
[API reference](https://pyomo.readthedocs.io/en/latest/api/pyomo.contrib.piecewise.transform.html).

## Challenges

1. Give the rising tiers a fourth breakpoint at 30 months with cost 1,450. Predict how many rows
   Pyomo writes for `"LB"`.
2. Run the MIS tool on the $2,600k cut with P010's must-do flag removed. Predict the rows it finds.
3. Use `find_infeasible_constraints` to check the plan of the $2,600k cut's LP relaxation against
   the MILP's rows. Which kind of row does it break?

## Design Note: Name the Formulation and the Solver's Limits in the Code

Two failures in this lesson only appear when the data changes: SOS2 works until a curve turns
concave, and the MIS tool explains until the conflict depends on integrality. Neither is a bug in
your rows. Write the choice down where the next reader sees it: pass `pw_repn` explicitly with a
comment on why, and have the infeasibility report say which model it explained (LP relaxation or
MILP) and which tool it used.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**contractor_tiers.py.** The contractor model with each `Piecewise` setting, and the rows Pyomo
wrote for the default (*Piecewise Writes*, *A Convex Cost*, *SOS2*). *Try:* Add `("rising tiers,
UB, INC", dict(cost=COST, constr_type="UB", repn="INC"))`. Predict the cost it reports.

- Program: [contractor_tiers.py](src/contractor_tiers.py)

**piecewise_bounds.py.** The rising tiers with `bought` bounded at the last breakpoint, past it,
and not at all (*Piecewise Writes*). *Try:* Add a breakpoint at 60 months with cost 3,550 and
predict what the second case buys.

- Program: [piecewise_bounds.py](src/piecewise_bounds.py)

**contractor_pwlf.py.** The same tiers with `PiecewiseLinearFunction` and three transformations
(*pyomo.contrib.piecewise*). *Try:* Use `contrib.piecewise.outer_repn_gdp` followed by `gdp.bigm`.

- Program: [contractor_pwlf.py](src/contractor_pwlf.py)

**iis_tools.py.** The MIS tool on the two budget cuts, and a plan checked against the cut model
(*The MIS Tool*, *find_infeasible_constraints*). *Try:* Print the whole report of the $2,600k cut
and find the first repair option it lists.

- Program: [iis_tools.py](src/iis_tools.py)

**write_iis_demo.py.** `write_iis` on the $2,600k cut: the error without a commercial solver, the
IIS rows with one (*write_iis*). *Try:* Pass `solver="cplex"` and read the error.

- Program: [write_iis_demo.py](src/write_iis_demo.py)
