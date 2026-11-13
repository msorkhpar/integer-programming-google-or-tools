# 6.1.3 At-Least-k, At-Most-k, Exactly-k

GridCap's rate-case team brings three numbers to the planning meeting. The Valley transmission yard
can stage at most 2 projects in the plan. The rate case promises every region at least 4 funded
projects. And the Coast vegetation crew is under contract for exactly 2 jobs, no more and no fewer.
Each is a statement about how many projects of a group the plan funds, which lesson 6.1.1 showed is
a linear expression. This lesson writes the three kinds of row, shows how each can make the model
impossible to solve and how to catch that before solving, compares two ways of writing "at most
one", and handles a rule that a count must be either zero or at least $`k`$, in four rules.

GridCap is a fictional utility's portfolio, generated for this course, and the numbers above are
invented for this lesson.

## At Most k, At Least k and Exactly k Are One Row Each on the Count

For a group of projects $`S \subseteq P`$ and a whole number $`k`$, the three rules are

```math
\sum_{i \in S} x_i \le k \quad \text{(at most } k\text{)}, \qquad
\sum_{i \in S} x_i \ge k \quad \text{(at least } k\text{)}, \qquad
\sum_{i \in S} x_i = k \quad \text{(exactly } k\text{)}
```

"Exactly" is "at most" and "at least" at once, which is why it is an equality. With $`k = 1`$ the
three have names you will meet in the literature: **at most one** is a *packing* row (the
alternative-group row $`\sum_{i \in g} x_i \le 1`$ of lesson 1.1.1 is one), **at least one** is a
*covering* row, and **exactly one** is a *partitioning* row, "choose one of these".

The three rate-case rules, on GridCap small:

```python
def count(sel, members):
    return sum(sel.x[i] for i in members)


def at_most(sel):         # the Valley transmission yard can stage at most 2 projects
    sel.model.add_linear_constraint(count(sel, ids(small, program="transmission", region="Valley")) <= 2,
                                    name="valley_yard")


def at_least(sel):        # the rate case promises every region at least 4 projects
    for r in REGIONS:
        sel.model.add_linear_constraint(count(sel, ids(small, region=r)) >= 4, name=f"promise_{r}")


def exactly(sel):         # the Coast vegetation crew is contracted for exactly 2 jobs
    sel.model.add_linear_constraint(count(sel, ids(small, program="vegetation", region="Coast")) == 2,
                                    name="coast_crew")
```

`at_least` writes one row per region, with the quantifier $`\forall r \in R`$; the other two are
single rows. Each rule is solved on its own, and the program prints the counts the rules talk
about:

```text
no rule  NPV $25,336k  Valley transmission 4, Ridge 3, Valley 7, Coast 7, Plains 3, Coast vegetation 3
at_most  NPV $24,793k  Valley transmission 2, Ridge 4, Valley 5, Coast 6, Plains 5, Coast vegetation 3
at_least NPV $25,317k  Valley transmission 4, Ridge 4, Valley 7, Coast 6, Plains 4, Coast vegetation 3
exactly  NPV $25,305k  Valley transmission 4, Ridge 3, Valley 6, Coast 5, Plains 4, Coast vegetation 2
```

The best plan without the rules funds 4 Valley transmission projects, 3 projects each in Ridge and
Plains, and 3 Coast vegetation jobs, so each rule cuts that plan off and the solver has to find
another:

- **At most 2** costs $543k: two Valley transmission projects leave, and the money goes to cheaper
  projects in other regions (Ridge rises from 3 to 4, Plains from 3 to 5).
- **At least 4 per region** costs only $19k: Ridge and Plains each gain a project, and Coast gives
  one up. A minimum is cheap when cheap projects can meet it.
- **Exactly 2** costs $31k. The Coast crew had 3 jobs in the best plan; "exactly" pushes the
  count down here. With a plan that had only 1 Coast vegetation job, the same row would push it up.
  An equality row cuts both ways, which is the reason to use it only when the business means both
  bounds.

## Check k Against What the Plan Must and Can Fund Before You Solve

A model none of whose plans satisfies every row is **infeasible**: the solver returns the status
`INFEASIBLE` and no plan at all. A counting row is the easiest way to make a model infeasible, and
it does so in two ways:

- **An at-least row asks for more than a plan can fund.** If a group has fewer candidates than
  $`k`$, no plan reaches $`k`$. Candidates that exclude each other count once: two projects in the
  same alternative group can never both be funded.
- **An at-most row allows fewer than the plan must fund.** If a group holds more must-do projects
  than $`k`$, every plan already exceeds $`k`$.

Both are checks on the data alone, so you can run them before building the model and report *which*
group and *which* number is wrong, something the solver's single word `INFEASIBLE` does not say.
The program tries three invented rules on GridCap small, "at least 2 vegetation projects per
region", "at least 2 transmission projects per region" and "at most 1 vegetation project per
region", with these checks:

```python
def most_choosable(members: list[str]) -> int:
    """How many of `members` one plan can fund: each alternative group counts once."""
    groups = {small.project(i).alt_group for i in members if small.project(i).alt_group}
    return sum(1 for i in members if not small.project(i).alt_group) + len(groups)


def precheck_cap(program: str, k: int) -> list[str]:
    problems = []
    for r in REGIONS:
        must = [i for i in ids(small, program=program, region=r) if small.project(i).must_do]
        if len(must) > k:
            problems.append(f"{r}: {len(must)} must-do projects {must}, cap {k}")
    return problems
```

```text
at least 2 vegetation projects per region: INFEASIBLE
  precheck: Plains: 1 candidate, at most 1 in one plan
at least 2 transmission projects per region: INFEASIBLE
  precheck: Plains: 2 candidates, at most 1 in one plan
at most 1 vegetation project per region: INFEASIBLE
  precheck: Valley: 2 must-do projects ['P003', 'P010'], cap 1
alternative groups: {'G001': ['P001', 'P002'], 'G030': ['P030', 'P031']}
```

The second case is the one a quick look gets wrong. Plains has two transmission candidates, P001
and P002, so "at least 2" looks possible; but they are the replace and repair options for the same
asset, alternative group G001, and a plan may fund only one of them.

The checks are **necessary, not sufficient**. A group can pass both and the model can still be
infeasible, because the projects the minimum needs do not fit the budget together with the
must-dos, or because two counting rows on overlapping groups pull against each other. When the
checks pass and the solver still says `INFEASIBLE`, the tools of section 9 find the smallest set of
rows that conflict.

The OR-Tools guide *Employee Scheduling* builds a nurse schedule from these three kinds of row and
nothing else. Four nurses cover three shifts a day for three days. Every shift gets exactly one
nurse, a partitioning row; no nurse works more than one shift a day, a packing row; and the nine
shifts are spread so that each nurse works at least $`\lfloor 9/4 \rfloor = 2`$ of them and at most
3, an at-least and an at-most row on each nurse's count. CP-SAT has the first two as constraints of
their own, `add_exactly_one` and `add_at_most_one`. `nurses.py` is the guide's model, with every
schedule counted instead of the first five printed:

```python
for d in DAYS:
    for s in SHIFTS:
        model.add_exactly_one(shifts[n, d, s] for n in NURSES)      # one nurse per shift
for n in NURSES:
    for d in DAYS:
        model.add_at_most_one(shifts[n, d, s] for s in SHIFTS)      # one shift per nurse and day
for n in NURSES:
    worked = sum(shifts[n, d, s] for d in DAYS for s in SHIFTS)
    model.add(worked >= min_shifts)                                 # at least k
    if max_shifts is not None:
        model.add(worked <= max_shifts)                             # at most k
```

```text
9 shifts, 4 nurses: each works at least 2 and at most 3
  min and max     OPTIMAL     5,184 schedules
  min only        OPTIMAL     5,184 schedules
  no spread rule  OPTIMAL    13,824 schedules
  min 3 each      INFEASIBLE      0 schedules
precheck for min 3: 4 nurses x 3 = 12 shifts wanted, 9 exist
```

The at-most row changes nothing here, as the guide says: four nurses with at least 2 of 9 shifts
each leave one shift over, so no nurse can reach 4. The at-least rows cut the schedules from 13,824
to 5,184. And "at least 3 each" is infeasible for the reason the first check above gives, counted
over a group of rows instead of one: the four minimums ask for 12 shifts and only 9 exist, which a
line of arithmetic shows before any solve.

<!-- practice 1 -->

## At Most One of Many Is One Row, Not One Row per Pair

Suppose the Valley transmission line can be taken out of service only once in the plan, so at most
one of the six Valley transmission projects may be funded. One way to write it says it pair by
pair, $`x_a + x_b \le 1`$ for every two projects $`a, b`$ of the group, which is the "not both" row
of lesson 6.1.2 repeated. Six projects make $`6 \cdot 5 / 2 = 15`$ pairs. The other way is the
single count row $`\sum_{i \in S} x_i \le 1`$:

```python
def at_most_one(sel, form: str) -> int:
    x = sel.x
    if form == "one row":
        sel.model.add_linear_constraint(sum(x[i] for i in valley) <= 1, name="valley_line")
        return 1
    pairs = list(itertools.combinations(valley, 2))
    for a, b in pairs:
        sel.model.add_linear_constraint(x[a] + x[b] <= 1, name=f"valley_{a}_{b}")
    return len(pairs)
```

Both allow exactly the same 0/1 plans: if two projects were funded, the pair row for those two
would fail, and so would the count row. So both MILPs have the same optimum. Their **LP
relaxations** (the same rows with each $`x_i`$ allowed anywhere between 0 and 1, lesson 3.1.1) are
not the same. The program solves each relaxation with GLOP and each MILP with HiGHS:

```text
Valley transmission projects: ['P022', 'P025', 'P030', 'P031', 'P032', 'P033']
one row   1 row   LP bound $24,197.20k  MILP $24,128k  gap $69.20k
         LP shares of the Valley projects: {'P030': 1.0}, sum 1.000
pairs    15 rows  LP bound $24,515.10k  MILP $24,128k  gap $387.10k
         LP shares of the Valley projects: {'P022': 0.5, 'P025': 0.5, 'P030': 0.5, 'P031': 0.5, 'P032': 0.5}, sum 2.500
```

With pair rows, the relaxation sets five projects to 0.5. No pair sums to more than 1, so every
pair row holds, and the group as a whole is "two and a half projects", which the business rule
forbids and the count row refuses. The pair form's LP bound is $387.10k above the true optimum; the
count row's is $69.20k above it. Lesson 3.1.2 called that distance the **integrality gap** and
showed why a smaller one helps: the solver's search (lessons 3.2.1 to 3.2.4) prunes with the LP bound, so a bound
closer to the optimum lets it discard more of the tree.

The count row is also one row instead of $`n(n-1)/2`$, which matters when a group has 50 members
(1,225 pairs). Merge pair rows into one count row whenever every pair in a group conflicts. When the
conflicts do not cover every pair (A conflicts with B and B with C, but A and C may go together),
the group is not a single "at most one", and only the pairs that really conflict can be written.


## None, or at Least k, Needs a Switch Variable

The vegetation contractor makes one last condition: it will go to a region only if it gets at least
2 vegetation jobs there. A region may have no vegetation work at all, or 2 or more, but not
exactly 1. That is not a single counting row, because the allowed counts, $`\{0, 2, 3, \dots\}`$, have a
hole in them. A new binary per region, $`g_r`$ ("the contractor goes to region $`r`$"), switches
between the two cases:

```math
\sum_{i \in V_r} x_i \ge k\, g_r \quad \text{(enough}_r\text{)}, \qquad
\sum_{i \in V_r} x_i \le |V_r|\, g_r \quad \text{(only\_if}_r\text{)}
```

with $`V_r`$ the vegetation projects of region $`r`$ and $`|V_r|`$ how many there are. Read the
two rows for each value of the switch:

- **$`g_r = 0`$**: the first row says the count is at least 0, which always holds; the second says
  it is at most 0. No vegetation work in $`r`$.
- **$`g_r = 1`$**: the first row says the count is at least $`k`$; the second says it is at most
  $`|V_r|`$, which always holds. At least $`k`$ jobs in $`r`$.

So each row is "switched off" in one case by being made trivially true, and the switch is the
solver's choice. $`|V_r|`$ in the second row is the largest the count can ever be; any smaller
number would cut off real plans, and lesson 6.2.1 makes that idea, choosing the smallest number
that is still safe, into a method.

```python
for r, members in vegetation.items():
    go[r] = model.add_binary_variable(name=f"go_{r}")
    jobs = sum(x[i] for i in members)
    model.add_linear_constraint(jobs >= K * go[r], name=f"enough_{r}")
    model.add_linear_constraint(jobs <= len(members) * go[r], name=f"only_if_{r}")
```

```text
without the rule: NPV $25,336k
  Ridge  3 candidates, funded ['P035']
  Valley 4 candidates, funded ['P003', 'P010', 'P018']
  Coast  4 candidates, funded ['P011', 'P014', 'P015']
  Plains 1 candidate , funded []
with the rule: NPV $25,317k
  Ridge  3 candidates, funded ['P008', 'P035']  go=1
  Valley 4 candidates, funded ['P003', 'P010', 'P018']  go=1
  Coast  4 candidates, funded ['P011', 'P012', 'P014']  go=1
  Plains 1 candidate , funded []  go=0
```

The best plan had exactly 1 vegetation job in Ridge, the case the contractor refuses. The solver
could drop P035 (to 0) or add a second Ridge job (to 2); adding P008 cost less, $19k in all
after the plan rebalanced elsewhere. Plains has only one vegetation candidate, so it can never reach
2, and the rule forces it to 0 for good; a precheck like the one above would flag that before the
solve.

The same two rows work with any upper limit: "none, or between $`k`$ and $`K`$" is
$`k\,g \le \text{count} \le K\,g`$. And they work with a weighted count, a total of kilometres or
units in place of a number of projects, as long as the second row uses the largest value that total
can take.

<!-- practice 2 -->

## The Model

The selection model on GridCap small with this lesson's rows marked. Each program adds one rule to
the base model; together they make this model.

**Sets.** $`P`$ the candidate projects; $`M`$, $`C`$ and $`\mathcal{G}`$ the must-do projects, the
child projects (parent $`p(c)`$) and the alternative groups; $`R`$ the regions; $`P_r \subseteq P`$
the projects in region $`r`$; $`T_{\text{Valley}}`$ the Valley transmission projects; $`V_r`$ the
vegetation projects in region $`r`$.

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ ($k); $`B = 38{,}390`$ ($k); $`k = 2`$, the
fewest vegetation jobs per region the contractor accepts.

**Variables.**

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(1 if project } i \text{ is funded)} \\
& g_r \in \{0, 1\} && \forall r \in R && \text{(1 if the contractor goes to region } r\text{)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{i \in T_{\text{Valley}}} x_i &\le 2 && && \text{(valley\_yard)} \quad \leftarrow \text{this lesson} \\
\sum_{i \in P_r} x_i &\ge 4 && \forall r \in R && \text{(promise}_r) \quad \leftarrow \text{this lesson} \\
\sum_{i \in V_{\text{Coast}}} x_i &= 2 && && \text{(coast\_crew)} \quad \leftarrow \text{this lesson} \\
\sum_{i \in V_r} x_i &\ge k\, g_r && \forall r \in R && \text{(enough}_r) \quad \leftarrow \text{this lesson} \\
\sum_{i \in V_r} x_i &\le |V_r|\, g_r && \forall r \in R && \text{(only\_if}_r) \quad \leftarrow \text{this lesson}
\end{aligned}
```

The clique program replaces `valley_yard` by "at most 1", written either as one row `valley_line`
or as 15 rows `valley_<a>_<b>`.

## Summary

- **At most k, at least k and exactly k are one row each on the count.** Exactly is both bounds;
  use it only when the business means both.
- **Check k against what the plan must and can fund before you solve.** Count candidates (each
  alternative group once) against an at-least $`k`$, and must-dos against an at-most $`k`$; the
  checks are necessary, not sufficient.
- **At most one of many is one row, not one row per pair.** The same 0/1 plans, a tighter LP
  bound ($69.20k against $387.10k of gap here), and far fewer rows.
- **None, or at least k, needs a switch variable.** $`k\,g \le \text{count} \le |S|\,g`$ with
  $`g`$ binary.

## Reference

| Rule in words | Row(s) |
| --- | --- |
| at most $`k`$ of $`S`$ | $`\sum_{i \in S} x_i \le k`$ |
| at least $`k`$ of $`S`$ | $`\sum_{i \in S} x_i \ge k`$ |
| exactly $`k`$ of $`S`$ | $`\sum_{i \in S} x_i = k`$ |
| at most one of $`S`$, every pair in conflict | $`\sum_{i \in S} x_i \le 1`$ (not $`x_a + x_b \le 1`$ per pair) |
| none, or at least $`k`$ | $`g \in \{0,1\}`$, $`\sum_{i \in S} x_i \ge k\,g`$, $`\sum_{i \in S} x_i \le \lvert S \rvert\,g`$ |
| none, or between $`k`$ and $`K`$ | $`k\,g \le \sum_{i \in S} x_i \le K\,g`$ |

| Precheck | Infeasible when |
| --- | --- |
| at least $`k`$ of $`S`$ | fewer than $`k`$ choosable in $`S`$ (each alternative group counts once) |
| at most $`k`$ of $`S`$ | more than $`k`$ must-do projects in $`S`$ |
| exactly $`k`$ of $`S`$ | either of the above |
| at least $`k_n`$ in each group $`n`$, every item counted in exactly one group | the $`k_n`$ add up to more than the items |

| CP-SAT | Row |
| --- | --- |
| `add_at_most_one(literals)` | $`\sum x_i \le 1`$ |
| `add_exactly_one(literals)` | $`\sum x_i = 1`$ |
| `add_bool_or(literals)` | $`\sum x_i \ge 1`$ |

**Further reading:** [Employee Scheduling (OR-Tools)](https://developers.google.com/optimization/scheduling/employee_scheduling) (the nurse example of `nurses.py`: exactly one nurse per shift, at most one shift per nurse and day, and a minimum and maximum number of shifts per nurse that spreads the work); [CP-SAT sample nurses_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/nurses_sat.py) (the same model as a complete program, with a solution callback that stops after five schedules); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1 names the multiple-choice row $`\sum x_j \le 1`$; section 9.2: "at least $`k`$ of $`p`$ constraints" with one binary per constraint, the switch idea of the last rule applied to rows); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2.2: two formulations of the same set can differ in the strength of their LP relaxation, as the pair rows and the count row do).

## Challenges

1. Rewrite "at least 4 projects in every region" as "at least 4, and at least one of them
   transmission". How many rows per region?
2. In `clique.py`, keep the pair rows but add the count row too. Predict the LP bound.
3. The contractor changes its terms: none, or between 2 and 3 jobs per region. Change
   `zero_or_k.py` and predict which region's plan changes.

## Design Note: Name the Group, Not the Pairs

Rules arrive from the business as pairs ("these two can't share an outage"), because that is how
engineers find them. Before writing them, gather the pairs into groups: if every two projects of a
group conflict, the group is one "at most one" row, and the model is smaller and its LP bound
tighter. Keep the pair list as the source the planners maintain, and let the model builder find the
groups. Lesson 6.7.2 treats this and other ways of strengthening rows as a topic of its own.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**cardinality.py.** Solves GridCap small with an at-most, an at-least and an exactly row, one at a
time (*At Most k, At Least k and Exactly k*). *Try:* Change the Coast rule to "exactly 4". Predict
whether the plan's NPV goes up or down.

- Program: [cardinality.py](src/cardinality.py)

**precheck.py.** Checks three counting rules against what the plan can and must fund, then solves
them (*Check k Against What the Plan Must and Can Fund*). *Try:* Ask for at least 2 distribution
projects per region. Predict what the precheck reports.

- Program: [precheck.py](src/precheck.py)

**clique.py.** Writes "at most one Valley transmission project" as one row and as 15 pair rows,
and compares the LP bounds (*At Most One of Many Is One Row*). *Try:* Use the four Coast
transmission projects instead. Predict whether the two LP bounds still differ.

- Program: [clique.py](src/clique.py)

**zero_or_k.py.** Adds the contractor's "none, or at least 2" rule with a switch variable per region
(*None, or at Least k, Needs a Switch Variable*). *Try:* Set `K = 3`. Predict which regions the
contractor goes to.

- Program: [zero_or_k.py](src/zero_or_k.py)

**nurses.py.** OR-Tools' nurse scheduling example in CP-SAT, with the number of schedules under
each spread rule and the minimum that leaves none (*Check k Against What the Plan Must and Can
Fund*). *Try:* Add a fifth nurse. Predict the minimum and maximum the program computes, and whether
the at-most row still changes nothing.

- Program: [nurses.py](src/nurses.py)
