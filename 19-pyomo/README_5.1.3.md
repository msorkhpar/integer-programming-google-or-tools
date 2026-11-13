# 5.1.3 Pyomo.GDP: Disjunctions, Big-M and Hull Transformations

Lesson 6.2.4 ordered three jobs that need the same substation outage in GridCap small's Coast
region: P011 (2 months), P016 (3) and P021 (5), within a 12-month year, finishing the jobs as early
as possible. "P011 before P016 **or** P016 before P011" is a **disjunction**, and that lesson wrote
it twice by hand, as big-M rows and as the hull, in MathOpt, with LP bounds of 10.00 and 13.98 and
an optimum of 17. Writing a form by hand is where a wrong M or a missing copy creeps in. Pyomo's
**GDP** (Generalized Disjunctive Programming) extension lets you state the disjunction once, as
logic, and have a **transformation** write either form for you. This lesson ports the outage model
to GDP, checks both forms against lesson 6.2.4's numbers, and shows what the transformations need
from you. GridCap is fictional, and the outage reading of `crew_months` is lesson 6.2.4's.

Lesson 6.2.4 is in section 6, which the course reaches later, and you do not need it here: *The
Model* below states the model in full, and the big-M and hull forms are explained where Pyomo
writes them. "Lesson 6.2.4's numbers" are the lines that lesson recorded from its two hand-written
MathOpt models, each solved as a MILP (with HiGHS) and as its LP relaxation (with GLOP):

<!-- unverified -->
```text
big_m  variables  6  rows  6  LP bound 10.00  MILP  17.0  starts {'P011': 0.0, 'P016': 2.0, 'P021': 5.0}
hull   variables 18  rows 24  LP bound 13.98  MILP  17.0  starts {'P011': 0.0, 'P016': 2.0, 'P021': 5.0}
```

An **LP bound** is the optimum of the **LP relaxation**, the same model with each binary allowed
anywhere in $`[0, 1]`$; for this minimization no plan can finish earlier than it. The module's tests
rebuild lesson 6.2.4's two MathOpt models and compare with them directly.

## The Model

**Sets.** $`J = \{\text{P011}, \text{P016}, \text{P021}\}`$ the jobs;
$`\Pi = \{(i, j) \in J \times J : i \text{ before } j \text{ in the list}\}`$ the pairs that share
the outage.

**Parameters.** $`d_j`$, job $`j`$'s duration in months (2, 3, 5); $`H = 12`$ months.

**Variables.** $`0 \le s_j \le H - d_j`$, the month job $`j`$ starts (continuous), for
$`j \in J`$. For each pair and each of its two disjuncts, a Boolean $`Y`$ that is true when that
disjunct holds; Pyomo creates these (`indicator_var`).

**Objective.**

```math
\min \; \sum_{j \in J} (s_j + d_j)
```

**Constraints.** For every pair, exactly one of two disjuncts holds:

```math
\big[\; Y^{0}_{ij} : s_i + d_i \le s_j \;\big] \;\veebar\; \big[\; Y^{1}_{ij} : s_j + d_j \le s_i \;\big] \qquad \forall (i, j) \in \Pi \qquad \text{(order}_{ij})
```

$`\veebar`$ is "exactly one of". This is the whole model: no M, no binary, no copy. Those are what a
transformation adds.

| Label | Pyomo |
| --- | --- |
| $`s_j`$ | `m.s[j]` |
| order$`_{ij}`$ | `m.order[i, j]`, a `Disjunction` with two disjuncts |
| $`Y^{0}_{ij}`$, $`Y^{1}_{ij}`$ | `m.order[i, j].disjuncts[0].indicator_var`, `...disjuncts[1].indicator_var` |

## A Disjunct Holds the Rows of One Option, and a Disjunction Picks Exactly One

A **disjunct** is a block of rows that hold together or not at all (here, one row each); a
**disjunction** groups disjuncts and says exactly one of them holds. The shortest way to write
one in Pyomo is a `Disjunction` whose rule returns a list of disjuncts, each a list of rows:

```python
m = pyo.ConcreteModel(name="outage GDP")
m.J = pyo.Set(initialize=list(durations))
m.pairs = pyo.Set(dimen=2, initialize=list(combinations(durations, 2)))
m.d = pyo.Param(m.J, initialize=durations)
m.s = pyo.Var(m.J, bounds=lambda m, j: (0, horizon - m.d[j]))      # start month

def order(m, i, j):
    return [[m.s[i] + m.d[i] <= m.s[j]],       # disjunct 0: i before j
            [m.s[j] + m.d[j] <= m.s[i]]]       # disjunct 1: j before i
m.order = Disjunction(m.pairs, rule=order)

m.finish = pyo.Objective(expr=sum(m.s[j] + m.d[j] for j in m.J), sense=pyo.minimize)
```

`Disjunction` comes from `pyomo.gdp`. Indexed by `m.pairs`, it is one disjunction per pair, and
Pyomo creates the disjuncts as `Disjunct` components behind it:

```text
order : Size=3, Index=pairs, Active=True
    Key              : Disjuncts                                    : Active : XOR
    ('P011', 'P016') : ['order_disjuncts[0]', 'order_disjuncts[1]'] :   True : True
    ('P011', 'P021') : ['order_disjuncts[2]', 'order_disjuncts[3]'] :   True : True
    ('P016', 'P021') : ['order_disjuncts[4]', 'order_disjuncts[5]'] :   True : True
```

`XOR: True` is the "exactly one" of $`\veebar`$, Pyomo's default for a disjunction. Each disjunct
has an `indicator_var`, a `BooleanVar` (true or false, not 0 or 1), which is how you read or fix
the choice. The disjuncts can also be declared one by one as `Disjunct` components with their own
constraints, and a disjunction built from them with `Disjunction(expr=[m.d1, m.d2])`; the list form
above is the same thing, shorter.

No solver can read this model yet: a MILP solver knows rows and integer variables, not "exactly one
of these blocks". A transformation rewrites it into a MILP, in place:
`pyo.TransformationFactory("gdp.bigm").apply_to(m)`.

## gdp.bigm Writes the Big-M Rows and Finds M From the Bounds

The big-M transformation gives each disjunct a binary, `binary_indicator_var`, adds one row per
disjunction saying the binaries sum to 1, and relaxes each disjunct's rows by an M when its binary
is 0 (lesson 6.2.1's switch). It computes each M from the variables' bounds, and you can read back
what it chose:

```python
milp = build(durations, HORIZON)
bigm = pyo.TransformationFactory("gdp.bigm")
bigm.apply_to(milp)
Ms = bigm.get_all_M_values_by_constraint(milp)
print(f"(lower M, upper M) of the {len(Ms)} disjunct rows:", set(Ms.values()))
row = milp.order["P011", "P016"].disjuncts[0].constraint[1]
print("P011 before P016 becomes:", bigm.get_transformed_constraints(row)[0].expr)
highs().solve(milp)
print(f"MILP {pyo.value(milp.finish):.1f}  starts {[round(milp.s[j].value, 2) for j in milp.J]}  first {first(milp)}")
```

```text
(lower M, upper M) of the 6 disjunct rows: {(None, 12.0)}
P011 before P016 becomes: s[P011] + 2 - s[P016] - 12.0*(1 - order_disjuncts[0].binary_indicator_var)  <=  0.0
MILP 17.0  starts [0.0, 2.0, 5.0]  first {('P011', 'P016'): 'P011', ('P011', 'P021'): 'P011', ('P016', 'P021'): 'P016'}
```

Every row got $`M = 12`$, the value lesson 6.2.4 derived by hand: with $`s_i \le H - d_i`$ and
$`s_j \ge 0`$, the most $`s_i + d_i - s_j`$ can be is $`H`$. (Each row has only an upper side, so
its lower M is `None`.) The transformed row is lesson 6.2.4's big-M row, with Pyomo's binary in
place of $`y_{ij}`$. The optimum is 17, shortest job first, and `first(m)` reads the order back from
the indicator variables:

```python
def first(m: pyo.ConcreteModel) -> dict[tuple[str, str], str]:
    """For each pair, the job the solution puts first, read from the disjuncts' indicator_var."""
    return {(i, j): i if m.order[i, j].disjuncts[0].indicator_var.value else j for i, j in m.pairs}
```

The M is only as good as the bounds. Remove one bound, and the transformation has nothing to
compute an M from. Both transformations raise `GDP_Error`, an exception class that `pyomo.gdp`
exports:

```python
import pyomo.environ as pyo
from pyomo.gdp import GDP_Error

for form in ("gdp.bigm", "gdp.hull"):
    m = build(durations, 12)
    m.s["P011"].setub(None)
    try:
        pyo.TransformationFactory(form).apply_to(m)
    except GDP_Error as error:
        print(f"{form}: GDP_Error: {str(error).splitlines()[0]}")
```

```text
gdp.bigm: GDP_Error: Cannot estimate M for unbounded expressions.
gdp.hull: GDP_Error: Variables that appear in disjuncts must be bounded in order to use the hull transformation! Missing bound for s[P011].
```

The first line is big-M's; the second is the hull's, which the next section explains.

You can then pass an M yourself, `apply_to(m, bigM=20)`, and the model solves (to 17 here). But a
hand-picked M is exactly lesson 6.2.2's risk: too small and it cuts off real plans, too large and
the LP bound and the numerics suffer, and nothing checks it for you. Bound the variables from the
data and let the transformation compute M.

<!-- practice 1 -->

## gdp.hull Writes a Copy per Disjunct and Needs Every Variable Bounded

The hull transformation writes lesson 6.2.4's other form: a copy of every variable a disjunct
mentions, per disjunct, bounded by the variable's bounds times that disjunct's binary, and the
original variable equal to the sum of its copies. One statement, two transformations, then each
model is solved as a MILP and as its LP relaxation:

```python
for form in ("gdp.bigm", "gdp.hull"):
    milp = build(durations, HORIZON)
    pyo.TransformationFactory(form).apply_to(milp)
    binaries = sum(1 for v in milp.component_data_objects(pyo.Var) if v.is_binary())
    size = f"{milp.nvariables()} variables ({binaries} binary), {milp.nconstraints()} rows"
    highs().solve(milp)
    best = pyo.value(milp.finish)
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(milp)
    highs().solve(milp)
    print(f"{form:9} {size}  LP bound {pyo.value(milp.finish):.2f}  MILP {best:.1f}")
```

```text
gdp.bigm  9 variables (6 binary), 9 rows  LP bound 10.00  MILP 17.0
gdp.hull  21 variables (6 binary), 27 rows  LP bound 13.98  MILP 17.0
```

The LP bounds are lesson 6.2.4's, 10.00 and 13.98, and the module's tests check both against the
MathOpt models of that lesson to $`10^{-6}`$. The hull is tighter for the reason that lesson gave:
each disjunction's LP region is the convex hull of its two orders. The sizes differ from the
hand-written ones (6 variables and 6 rows for big-M, 18 and 24 for the hull) because Pyomo gives
each **disjunct** its own binary, 6 instead of lesson 6.2.4's one $`y_{ij}`$ per pair, and adds a
row per pair making the two sum to 1. The hull's 21 variables are those 9 plus 12 copies: two starts
in each of the six disjuncts.

The order of the two transformations matters when you want an LP bound. The binaries do not exist
until the GDP transformation creates them, so relaxing first relaxes nothing:

```python
early = build(durations, HORIZON)
pyo.TransformationFactory("core.relax_integer_vars").apply_to(early)
pyo.TransformationFactory("gdp.hull").apply_to(early)
highs().solve(early)
print(f"relax, then gdp.hull: 'LP bound' {pyo.value(early.finish):.2f}")
```

```text
relax, then gdp.hull: 'LP bound' 17.00
```

That "LP bound" is the MILP optimum, solved with binaries intact. Transform, then relax.

The hull needs bounds even more than big-M does, because each copy's bound is the variable's bound
times the switch. With the bound on $`s_{P011}`$ removed, the loop above printed for the hull too:

```text
gdp.hull: GDP_Error: Variables that appear in disjuncts must be bounded in order to use the hull transformation! Missing bound for s[P011].
```

and the hull has no `bigM=` escape. The trade-off is lesson 6.2.4's: the hull is tighter and
bigger; for a disjunction over one variable's intervals a tight big-M is already as tight; when
disjuncts tie several variables together, compare the two LP bounds, which with GDP costs one
argument. Pyomo has other transformations too (its documentation lists a multiple-big-M
`gdp.mbigm` and a cutting-plane `gdp.cuttingplane`, among others); this lesson does not use them.

<!-- practice 2 -->

## Planner Rules Go on the Disjuncts' Booleans

The indicator variables are model variables like any other, so a planner's rule about the choices
is written on them. Fixing one fixes a choice: the planners want P021, the longest job, out of the
way first, before P011:

```python
m = build(durations, 12)
m.order["P011", "P021"].disjuncts[1].indicator_var.fix(True)
print("P021 before P011:          ", solve(m))
```

A rule that links choices is a `LogicalConstraint` over the Booleans, with `.implies(...)`, `&`,
`|`, `~` and the counting functions `atleast`, `atmost` and `exactly`. "If P021 goes before P011, it
goes before P016 too":

```python
before_011 = m.order["P011", "P021"].disjuncts[1].indicator_var
before_016 = m.order["P016", "P021"].disjuncts[1].indicator_var
m.lead = pyo.LogicalConstraint(expr=before_011.implies(before_016))
print("... and then before P016:  ", solve(m))
```

```text
P021 before P011:           21  starts [8.0, 0.0, 3.0]  first {('P011', 'P016'): 'P016', ('P011', 'P021'): 'P021', ('P016', 'P021'): 'P016'}
... and then before P016:   22  starts [5.0, 7.0, 0.0]  first {('P011', 'P016'): 'P011', ('P011', 'P021'): 'P021', ('P016', 'P021'): 'P021'}
```

With only the fixed choice, the best order is P016, P021, P011 (finishes 3, 8 and 10, sum 21): P021
goes before P011 but not first. With the logical rule, P021 must lead both, and the order is P021,
P011, P016 (finishes 5, 7 and 10, sum 22). The same `gdp.bigm` call turned the logical rule into
rows on the binaries; nothing else changed in the code. (`solve` in `gdp_rules.py` applies
`gdp.bigm`, solves, and prints the objective, starts and order.)

## Summary

- **A disjunct holds the rows of one option, and a disjunction picks exactly one.**
  `Disjunction(m.pairs, rule=...)` returning a list of lists; each disjunct's `indicator_var` is a
  Boolean.
- **gdp.bigm writes the big-M rows and finds M from the bounds.** M = 12 on every outage row, lesson
  6.2.4's value; no bound, no M (`GDP_Error`), and a hand-given `bigM=` is unchecked.
- **gdp.hull writes a copy per disjunct and needs every variable bounded.** LP bounds 10.00 (big-M)
  and 13.98 (hull), equal to lesson 6.2.4's; transform before you relax.
- **Planner rules go on the disjuncts' Booleans.** Fix an `indicator_var`, or write a
  `LogicalConstraint`; the transformation handles both.

## Reference

| Step | Code |
| --- | --- |
| a disjunction | `from pyomo.gdp import Disjunction`; `m.d = Disjunction(I, rule=lambda m, i: [[row, ...], [row, ...]])` |
| big-M | `pyo.TransformationFactory("gdp.bigm").apply_to(m)`; `apply_to(m, bigM=M)` to override |
| hull | `pyo.TransformationFactory("gdp.hull").apply_to(m)` (every variable in a disjunct bounded) |
| LP bound | transform, then `pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)`, then solve |
| M chosen | `bigm.get_all_M_values_by_constraint(m)`, `bigm.get_transformed_constraints(row)` |
| read the choice | `m.d[i].disjuncts[k].indicator_var.value` (True or False) |
| fix a choice | `m.d[i].disjuncts[k].indicator_var.fix(True)` |
| logic | `pyo.LogicalConstraint(expr=Y1.implies(Y2))`, `&`, `|`, `~`, `atleast`, `atmost`, `exactly` |

| Form | Per disjunction (Pyomo) | LP relaxation | Needs |
| --- | --- | --- | --- |
| `gdp.bigm` | a binary per disjunct, a sum-to-1 row | as weak as its M | bounds, or a hand-given M |
| `gdp.hull` | the same, plus a copy of each variable per disjunct and its rows | the convex hull of each disjunction | every variable bounded |

**Further reading.** Pyomo documentation, [Generalized Disjunctive Programming](https://pyomo.readthedocs.io/en/stable/explanation/modeling/gdp/index.html),
in particular [Modeling in Pyomo.GDP](https://pyomo.readthedocs.io/en/stable/explanation/modeling/gdp/modeling.html)
(the explicit, indexed and list forms of a disjunction; `indicator_var` as a Boolean;
`LogicalConstraint` and its operators) and [Solving Logic-based Models with Pyomo.GDP](https://pyomo.readthedocs.io/en/stable/explanation/modeling/gdp/solving.html)
(`gdp.bigm` and how it estimates M or takes it from `bigM`, `gdp.hull` and its bounded-variable
requirement, `gdp.mbigm` and `gdp.cuttingplane`). MO-book,
[3.5 Machine scheduling](https://mobook.github.io/MO-book/notebooks/03/05-machine-scheduling.html):
the same no-overlap disjunction in Pyomo.GDP, transformed with a hand-picked M.

## Challenges

1. Add a fourth outage job of 4 months. Predict the MILP and which LP bound moves more, then run
   both transformations.
2. Write the outage disjunctions with explicit `Disjunct` components (one per order) and an indexed
   `Disjunction(expr=[...])`, and check the bounds do not change.
3. Write "P016 is not last" as a `LogicalConstraint` with `atleast`.

## Design Note: State the Logic, Choose the Form Later

Lesson 6.2.4 kept the business rule and its form apart by hand (`add_big_m`, `add_hull`). GDP makes
that separation the language: the model says "one of these orders holds", and one line chooses how
a MILP solver sees it. The habit that goes with it is to compare forms by their LP bound and size
before committing, which here was a loop over two transformation names.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**gdp_forms.py.** The outage disjunctions transformed by `gdp.bigm` and `gdp.hull`, solved as MILP
and as LP, with the M values and one transformed row (*A Disjunct Holds the Rows*, *gdp.bigm*,
*gdp.hull*). *Try:* Make the horizon 24 months. Predict the M values, then which LP bound moves.

- Program: [gdp_forms.py](src/gdp_forms.py)

**gdp_rules.py.** What happens without a bound, a hand-given M, and planner rules on the indicator
variables (*gdp.bigm*, *gdp.hull*, *Planner Rules*). *Try:* Fix P011 to go last instead. Predict
the objective.

- Program: [gdp_rules.py](src/gdp_rules.py)

**outage_gdp.py.** The GDP model builder and `first`, which reads the order.

- Library: [outage_gdp.py](src/outage_gdp.py)
