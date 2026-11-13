# 11.1.2 Vectorized Model Building From DataFrames

GridCap's planning data does not arrive as Python objects. It arrives as an export from the
planning database: flat tables, one row per project, one row per start year with its NPV, one row
per year of budget. The team's builder reads those tables into pandas and walks them row by row,
and lesson 11.1.1 measured the result: most of a minute for the large portfolio, spent mostly in
pandas, asking the same question of a whole table thousands of times. This lesson rebuilds the same
model from the same tables in about a tenth of a second, and proves it is the same model.

## The Model

The timing model of lessons 6.4.1 and 6.4.2, unchanged; the lesson changes only how it is built.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} - \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} &\le 0 && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The after row is written with every variable on the left, the way MathOpt stores it (lesson 4.2.1):
$`+1`$ on the child's starts up to $`t`$, $`-1`$ on the parent's starts up to $`t - L_c`$.

## Read the Data as Tables, One Row per Fact

`gridcap.save_csv` writes a portfolio as the flat files a planning export has (lesson 1.3.1 read
them into pandas). `tables.py` reads the four the timing model needs into a `Tables` object:
`projects` (one row per project), `starts` (one row per allowed start year, with its NPV), `costs`
(one row per year of work) and `budget` (one row per year). The projects file stores each cost
profile as one text cell, `"1320;1320"`; a model needs one row per year of work, so the reader
splits the text into a list and turns each list element into a row of its own:

```python
    costs = (projects[["project_id", "cost_profile"]]
             .assign(amount=projects["cost_profile"].str.split(";"))
             .explode("amount")
             .drop(columns="cost_profile"))
    costs["amount"] = costs["amount"].astype("int64")
    costs["k"] = costs.groupby("project_id").cumcount()
```

`explode` repeats a row once per element of a list cell, and `groupby(...).cumcount()` numbers the
rows of each project 0, 1, 2, ..., which is exactly $`k`$, the year of work. The file is read with
`keep_default_na=False`, so a project with no parent has the empty text `""` in `parent`, not a
missing value, and a test like `parent != ""` means "has a parent". On GridCap small:

```text
project_id region  earliest_start  latest_start  must_do parent  parent_lag alt_group
      P001 Plains            2028          2030    False                  0      G001
      P002 Plains            2027          2028    False                  0      G001
      P003 Valley            2031          2031     True                  0          
      P004 Plains            2028          2028    False                  0          

project_id  start  npv
      P001   2028 1401
      P001   2029 1189
      P001   2030 1002
      P002   2027  386

project_id  k  amount
      P001  0    1320
      P001  1    1320
      P002  0     460
      P003  0     140

 year  budget
 2027    8890
 2028    8120
 2029    8760
 2030    8610
 2031    7850

40 projects, 80 start rows, 57 cost rows, 5 years
```

The `starts` table is already the list of variables: one row per $`x_{i,t}`$, in the order the
loop builder creates them (projects in order, start years ascending). Every coefficient of the
model is a fact in one of these tables, or a join of two of them.

## Every Row Family Is a Table of (row, column, coefficient)

A linear model is a sparse matrix (lesson 1.2.2): each constraint is a row, each variable a column,
and only the nonzero coefficients are stored. So build the matrix the way pandas likes to work, as
a table with one line per nonzero, `(row, col, coef)`, computed for a whole family of rows at once
with joins and filters instead of loops.

First the columns. Variable number `col` is row number `col` of the `starts` table:

```python
    cols = t.starts[["project_id", "start", "npv"]].copy()
    cols["col"] = np.arange(len(cols))
    cols["name"] = "x_" + cols["project_id"] + "_" + cols["start"].astype(str)
```

The budget family is one join. Every start variable pays its project's whole cost profile, shifted
to its start year, so join the columns to the cost rows on `project_id`; the year that cost lands in
is `start + k`, and that year is the row's key:

```python
    budget = t.budget.assign(key=t.budget["year"].astype(str), name="budget_" + t.budget["year"].astype(str),
                             lb=-INF, ub=t.budget["budget"].astype(float))
    spend = cols[["project_id", "start", "col"]].merge(t.costs, on="project_id")
    spend["key"] = (spend["start"] + spend["k"]).astype(str)
    budget_terms = spend[["key", "col"]].assign(coef=spend["amount"].astype(float))
```

That is $`c_{i,y-t}`$ for every $`(i, t, y)`$ at once: the join pairs each $`x_{i,t}`$ with each
$`c_{i,k}`$, and $`y = t + k`$. A cost that would land after the plan's last year finds no budget
row and is dropped when the terms are matched to rows; GridCap's windows are cut so that never
happens.

The after family is two joins with a filter each. One row per child and child start $`t`$; then
$`+1`$ on the child's own starts $`u \le t`$, and $`-1`$ on the parent's starts
$`s \le t - L_c`$:

```python
    kids = p.loc[p["parent"] != "", ["project_id", "parent", "parent_lag"]]
    rows = kids.merge(cols[["project_id", "start"]], on="project_id")
    rows["key"] = rows["project_id"] + "@" + rows["start"].astype(str)
    after = rows.assign(name="after_" + rows["project_id"] + "_" + rows["start"].astype(str), lb=-INF, ub=0.0)
    mine = rows.merge(cols[["project_id", "start", "col"]], on="project_id", suffixes=("", "_u"))
    mine = mine[mine["start_u"] <= mine["start"]].assign(coef=1.0)
    theirs = rows.merge(cols[["project_id", "start", "col"]].rename(columns={"project_id": "parent"}),
                        on="parent", suffixes=("", "_s"))
    theirs = theirs[theirs["start_s"] <= theirs["start"] - theirs["parent_lag"]].assign(coef=-1.0)
    after_terms = pd.concat([mine, theirs])[["key", "col", "coef"]]
```

The `once`/`must` and `alt` families are the same idea with no filter. Each family gives a table of
rows (`key`, `name`, `lb`, `ub`) and a table of terms (`key`, `col`, `coef`); `entries` numbers the
rows family by family, in the loop builder's order (once and must, alt, after, budget), and swaps
each term's `key` for its row number. On GridCap small, with the entries of one child's row:

```text
80 columns, 49 rows, 210 entries; rows per family: {'once': 36, 'must': 4, 'alt': 2, 'after': 2, 'budget': 5}

P016 follows P015 with lag 0; its rows' entries:
 row            name  col    name_var  coef
  42 after_P016_2030   26 x_P015_2029  -1.0
  42 after_P016_2030   27 x_P015_2030  -1.0
  42 after_P016_2030   28 x_P016_2030   1.0
```

P016 may start only in 2030, so it has one after row: $`x_{P016,2030} - x_{P015,2029} - x_{P015,2030}
\le 0`$, "P016 starts in 2030 only if P015 started by 2030". That is the formulation's
$`\text{after}_{c,t}`$ with $`L_c = 0`$, read straight off the table.

<!-- practice 1 -->

## Hand MathOpt the Whole Matrix as a ModelProto

MathOpt's Python objects (`Variable`, `LinearConstraint`) are created one call at a time, which is
the per-row cost pandas just avoided. But a model also has a second form: the `ModelProto`, the
protocol buffer that `mathopt.solve` exports and hands to the solver (lesson 11.1.1). Its fields are
arrays: variable ids, bounds, integer flags and names; row ids, bounds and names; and the matrix as
three parallel arrays, `row_ids`, `column_ids` and `coefficients`. `Model.from_model_proto` builds a
`Model` from one. So the builder fills the arrays from the tables:

```python
def build_matrix(t: Tables) -> mathopt.Model:
    cols = columns(t)
    rows, terms = entries(cols, t)
    terms = terms[terms["coef"] != 0].sort_values(["row", "col"], kind="stable")   # row-major, no zeros

    proto = model_pb2.ModelProto(name=f"{t.name} timing")
    proto.variables.ids.extend(cols["col"].tolist())
    proto.variables.lower_bounds.extend([0.0] * len(cols))
    proto.variables.upper_bounds.extend([1.0] * len(cols))
    proto.variables.integers.extend([True] * len(cols))
    proto.variables.names.extend(cols["name"].tolist())
    proto.linear_constraints.ids.extend(rows["row"].tolist())
    proto.linear_constraints.lower_bounds.extend(rows["lb"].tolist())
    proto.linear_constraints.upper_bounds.extend(rows["ub"].tolist())
    proto.linear_constraints.names.extend(rows["name"].tolist())
    proto.linear_constraint_matrix.row_ids.extend(terms["row"].tolist())
    proto.linear_constraint_matrix.column_ids.extend(terms["col"].tolist())
    proto.linear_constraint_matrix.coefficients.extend(terms["coef"].tolist())
    objective = cols[cols["npv"] != 0]
    proto.objective.maximize = True
    proto.objective.linear_coefficients.ids.extend(objective["col"].tolist())
    proto.objective.linear_coefficients.values.extend(objective["npv"].astype(float).tolist())
    return mathopt.Model.from_model_proto(proto)
```

A proto is only valid if it keeps the rules written in OR-Tools' `model.proto` and
`sparse_containers.proto`, and the builder keeps each one on purpose:

| Rule | How the builder keeps it |
| --- | --- |
| variable and row ids are nonnegative and strictly increasing | `np.arange` for columns; rows numbered in order |
| nonempty names are distinct | names come from unique keys: project and start, family and key |
| matrix entries in row-major order, no `(row, col)` pair twice | `sort_values(["row", "col"])`; each join gives a pair once |
| every row and column id in the matrix exists | terms are matched to rows by `merge`, which drops a term with no row |
| an entry not listed is zero | zero coefficients are left out (the proto's comments call a listed zero wasted space) |

What happens when a rule is broken? `proto_rules.py` exports a two-variable model ($`x + 2y \le 2`$,
row `r`), breaks it four ways, and loads each copy:

```text
an explicit 0.0 for z      loaded; row r holds [('r', 'x', 1.0), ('r', 'y', 2.0)]
row entries out of order   refused, ValueError: column_ids should be strictly increasing within a row, but for row_id: 0 found [1, 0] at indices, [0, 1]
variable ids decreasing    refused, ValueError: Expected ids to be strictly increasing, but at index 1 found id: 0 and at previous index 0 found id: 1
two variables named x      loaded; row r holds [('r', 'x', 1.0), ('r', 'x', 2.0)]
... then solved            refused: duplicate name inserted: x
```

- **A listed zero is dropped on loading**, as MathOpt drops a zero coefficient added call by call
  (lesson 4.2.1): row `r` has no entry for the new variable `z`. So a stray zero cannot make two
  equal models export differently; the builder leaves zeros out anyway, since they are waste.
- **Order and ids are checked when the proto is loaded**, with an error that names the rule. Forget
  the sort and `from_model_proto` refuses the model at once.
- **Names are checked only at solve time**, as they are for a model built call by call (lesson
  4.2.1): the twin `x` loads and the solve refuses it, far from the line that made it. A builder that
  makes names from data must make them unique itself.

The model that comes back has no Python dictionary of variables, so read the plan through the
column numbers: `model.get_variable(col)` returns the variable whose id is `col`. The program solves
the small model it built:

```python
    x = {(r.project_id, r.start): model.get_variable(r.col) for r in cols.itertuples()}
    plan = sorted(key for key, var in x.items() if result.variable_values(var) > 0.5)
```

```text
OPTIMAL, NPV 24,260k, 27 projects started; first three: [('P001', 2028), ('P003', 2031), ('P005', 2029)]
```

$24,260k is the NPV lesson 6.4.2 found for this model built by loops, as it must be: by the next
section, it is the same model.

## A Fast Builder Is Correct Only If Its Exported Model Equals the Slow One's

Speed is worth nothing if the fast builder makes a different model: a budget row off by a year
solves happily and plans the wrong work. So a rewrite of a builder comes with a test that the new
model is the old model, and MathOpt gives a precise one. `export_model()` returns the whole model
as one `ModelProto`, and two protos compare equal with `==` only if every id, name, bound, integer
flag, matrix entry and objective coefficient agrees. The test needs no solver and no tolerance:

```python
        reference = build_loops(portfolio).export_model()
        same = {name: build(tables).export_model() == reference
                for name, build in (("slow", build_slow), ("matrix", build_matrix))}
```

```text
small :     80 variables,     49 rows; identical to build_loops: slow True, matrix True
medium:    887 variables,    469 rows; identical to build_loops: slow True, matrix True
large : 21,843 variables, 11,467 rows; identical to build_loops: slow True, matrix True
```

Three builders written three ways make byte-for-byte the same model on all three sizes. The
module's tests run the same comparison at two more seeds of the medium portfolio.

Proto equality is strict about order, too: variable 0 must be the same variable in both. When a
check fails, `==` says only "different". `same_model.py` then compares the models **by name**:
`canonical` turns a model into dictionaries keyed by variable and row names, which leaves out the
order things were added in, and `differences` lists the names that disagree.

```python
def canonical(model: mathopt.Model) -> dict:
    """The model keyed by names: what it says, with the order things were added left out."""
    objective = model.objective
    return {
        "variables": {v.name: (v.lower_bound, v.upper_bound, v.integer) for v in model.variables()},
        "rows": {c.name: (c.lower_bound, c.upper_bound,
                          {t.variable.name: t.coefficient for t in c.terms()})
                 for c in model.linear_constraints()},
        "objective": (objective.is_maximize, objective.offset,
                      {t.variable.name: t.coefficient for t in objective.linear_terms()}),
    }
```

The program compares the loop builder's small model with three others: the matrix builder's; the
matrix builder fed the `starts` table sorted by year first, so its variables come in another order;
and the matrix builder fed cost rows shifted one year late, the off-by-one a rewrite can introduce:

```text
matrix builder:      protos equal: True | differences by name: []
variables year-first: protos equal: False | differences by name: []
costs one year late:  protos equal: False
   row budget_2027: [-inf, 8890] 10 terms: 460*x_P002_2027 + 360*x_P022_2027 + ... vs [-inf, 8890] 0 terms
   row budget_2028: [-inf, 8120] 20 terms: 1320*x_P001_2028 + 460*x_P002_2028 + ... vs [-inf, 8120] 10 terms: 460*x_P002_2027 + 360*x_P022_2027 + ...
   row budget_2029: [-inf, 8760] 26 terms: 1320*x_P001_2028 + 1320*x_P001_2029 + ... vs [-inf, 8760] 20 terms: 1320*x_P001_2028 + 460*x_P002_2028 + ...
```

Read the three lines together:

- **Equal protos settle it.** The matrix model is the loop model.
- **Unequal protos with no differences by name** mean the same model in another order. It solves to
  the same optimum, but a test that wants byte equality must build in the reference's order, which
  is why `entries` numbers rows family by family exactly as the loop builder adds them.
- **Differences by name** are a real bug, and they say where: the 2027 budget row lost every term,
  and each later row holds the previous year's costs.

Comparing by name with `==` on coefficients works here because both builders compute every
coefficient from the same integers. When two builders compute a coefficient by different
arithmetic (a discount factor multiplied in a different order, say), the floats can differ in the
last digit while the models mean the same thing; then compare coefficients with a small relative
tolerance, as lesson 1.3.3 does for numbers in tests, and keep bounds, integer flags and names exact.

<!-- practice 2 -->

<!-- practice 3 -->

## Vectorizing Pays at Scale and Costs on Small Models

With the identity settled, the timings mean something. `speedup.py` times all three builders in
one process, five repeats each after a warm-up (one repeat for the slow builder on large, which
takes most of a minute). One run on the author's machine; yours will differ:

<!-- unverified -->
```text
measured (median seconds; speed-up over the slow builder):
small : slow   0.082   loops  0.002 (   41x)   matrix  0.018 (    5x)
medium: slow   0.759   loops  0.047 (   16x)   matrix  0.043 (   18x)
large : slow  34.212   loops  0.684 (   50x)   matrix  0.111 (  307x)
```

- **At 10,000 projects the matrix builder is about 300 times faster than the slow builder** and
  about 6 times faster than the loops. It builds GridCap large in about a tenth of a second, the
  section's milestone of a large portfolio "built in seconds" with room to spare.
- **On small, the matrix builder is the slower of the two fast ones.** Each pandas operation has a
  fixed cost, and the matrix builder does a few dozen of them whatever the size; with 80 variables
  that fixed cost is all there is, so the loops win, 0.002 s against 0.018 s.
- **The loop builder is fast because it has no hidden scans.** It walks Python objects it already
  has, with dictionary lookups. The slow builder's problem was never Python loops as such; it was
  a full-table scan inside a loop (lesson 11.1.1).

So the order of work for a slow builder is: measure, find the repeated scan, replace it with a join
or a dictionary built once, check the exported model is unchanged, and only then measure again.
Most of the speed comes from the first fix; going all the way to arrays pays when the model is
large or rebuilt often.

## Summary

- **Read the data as tables, one row per fact.** `explode` and `groupby(...).cumcount()` turn a
  packed cost profile into one row per year of work; the `starts` table is the list of variables.
- **Every row family is a table of (row, column, coefficient).** Joins pair variables with the
  data that gives their coefficients, and filters keep the pairs a row's quantifier allows.
- **Hand MathOpt the whole matrix as a `ModelProto`.** `Model.from_model_proto` takes arrays; the
  proto's rules (increasing ids, distinct names, row-major entries) are the builder's to keep, and
  zeros are dropped.
- **A fast builder is correct only if its exported model equals the slow one's.** `export_model()`
  compared with `==` needs no solver; when it fails, a comparison by name says what differs.
- **Vectorizing pays at scale and costs on small models.** 300 times faster than the slow builder on
  GridCap large, slower than plain loops on GridCap small.

## Reference

| pandas | What it does here |
| --- | --- |
| `s.str.split(";")` then `df.explode(col)` | one row per element of a packed list |
| `df.groupby(key).cumcount()` | 0, 1, 2, ... within each key: the year of work $`k`$ |
| `a.merge(b, on=key)` | pairs every row of `a` with every row of `b` that shares the key |
| `df[df[x] <= df[y]]` | keeps the pairs a quantifier allows |
| `df.itertuples()` | walks rows as named tuples, far cheaper than `iterrows` |

| MathOpt | What it does |
| --- | --- |
| `model_pb2.ModelProto` | a model as arrays (`from ortools.math_opt import model_pb2`) |
| `mathopt.Model.from_model_proto(proto)` | a `Model` equal to the proto |
| `model.export_model()` | the model as a `ModelProto`; compare two with `==` |
| `model.get_variable(id)` | the variable with that id |

**Further reading:** [MathOpt `model.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/model.py) (`Model.from_model_proto` and `export_model`, the two ends of a proto round trip); [MathOpt `model.proto` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/model.proto) (the fields of a model and their rules: increasing ids, distinct nonempty names, finite coefficients, unlisted entries are zero); [MathOpt `sparse_containers.proto` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/sparse_containers.proto) (row-major matrix entries, each pair once; sorted vector ids); [MathOpt `solve.py` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/python/solve.py) (every solve exports the model to this proto); [pandas `DataFrame.explode`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html) (one row per list element, the index repeated); [pandas `DataFrame.iterrows`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html) (why walking rows as Series is slow, and `itertuples`).

## Challenges

1. Add the regional caps of lesson 6.5.5 to the matrix builder as a fifth family. Which join gives
   the region of each term, and what is the row's key?
2. `build_matrix` puts the terms of every family into one table before sorting. What would go wrong
   if it sorted each family's terms on its own and concatenated them?
3. Replace `starts_of`'s mask in `build_slow` with a dictionary built once by `groupby`, and nothing
   else. Measure: how much of the 300 times does that one change win back?

## Design Note: Keep a Slow, Obvious Builder as the Reference

The matrix builder is harder to read than the loop builder: the after family is two joins and two
filters where the formulation has two sums. That is the price of speed, and the reason this module
keeps `build_loops` around even though it is never the fastest. It reads like the formulation, so a
reviewer can check it against The Model line by line, and the identity test then carries that
review over to the fast builder for free. When the model changes, change the obvious builder
first, then make the fast one equal it again.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change. The timings you get are your machine's, and they will differ from the ones on this page.

**tables.py.** GridCap written as CSV and read back into the four tables the model needs (*Read the Data as Tables*). *Try:* Print `t.costs` for a project with a three-year profile. Which column is $`k`$?

- Program: [tables.py](src/tables.py)

**matrix_builder.py.** The column table, the four row families as entry tables, the `ModelProto` and a solve of GridCap small (*Every Row Family Is a Table*, *Hand MathOpt the Whole Matrix*). *Try:* Print the entries of a budget row and check one coefficient against `t.costs` by hand.

- Program: [matrix_builder.py](src/matrix_builder.py)

**proto_rules.py.** A two-variable model's proto broken four ways and loaded again: which rules are checked on loading, which at solve time (*Hand MathOpt the Whole Matrix*). *Try:* List row `r`'s entries twice for the same variable and predict whether loading accepts it.

- Program: [proto_rules.py](src/proto_rules.py)

**same_model.py.** Proto equality, then a comparison by name, on a reordered model and on one with an off-by-one (*A Fast Builder Is Correct Only If*). *Try:* Change the `once` rows' upper bound to 2 in a copy of `entries` and predict what `differences` prints.

- Program: [same_model.py](src/same_model.py)

**speedup.py.** The three builders checked identical and then timed on small, medium and large (*Vectorizing Pays at Scale*). *Try:* Before running, guess which builder is fastest on medium on your machine.

- Program: [speedup.py](src/speedup.py)

**loop_builder.py, slow_builder.py.** The reference builder and the slow DataFrame builder, from lesson 11.1.1.

- Library: [loop_builder.py](src/loop_builder.py)
- Library: [slow_builder.py](src/slow_builder.py)
