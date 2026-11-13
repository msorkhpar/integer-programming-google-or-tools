# 6.1.2 AND, OR, NOT, XOR and Implication as Linear Constraints

GridCap's engineers have sent the planning team four rules about the small portfolio, written the
way engineers write them:

- "P030 and P032 both need the same Valley line out of service. Fund one or the other, not both."
- "Replacing the Ridge towers in P028 means P024 has to be built too, to carry the Ridge load."
- "If P022 and P025 are both funded, the Valley yard is overloaded unless P033 rebuilds it."
- "Undergrounding P034 needs one of the Plains replacements, P013 or P040."

Each sentence is logic: *not both*, *if … then*, *if both … then*, *needs one of*. A MILP has no
logic operators, only linear rows over numbers. This lesson shows that with 0/1 variables every one
of these sentences is a linear row, how to check that a row says what you mean, and when a piece of
logic needs a variable of its own, in five rules.

GridCap is a fictional utility's portfolio, generated for this course; the four rules above are
invented for this lesson.

## NOT Is One Minus the Binary

Write $`a`$ for the statement "project $`a`$ is funded". Its binary $`x_a`$ is 1 when the statement
is true and 0 when it is false, so **the binary is the statement's truth value**. That one fact is
what makes logic linear.

The statement "project $`a`$ is *not* funded" is true exactly when $`x_a = 0`$. Its truth value is
therefore

```math
\text{NOT } a \;=\; 1 - x_a
```

which is 1 when $`x_a = 0`$ and 0 when $`x_a = 1`$. It is a linear expression, so it can stand
anywhere $`x_a`$ can. Every rule below that mentions "not" is written by putting $`1 - x`$ where the
statement appears and then moving terms so the row reads cleanly.

## An Implication Between Two Decisions Is One Inequality

"If $`a`$ then $`b`$", written $`a \Rightarrow b`$, forbids exactly one combination: $`a`$ true and
$`b`$ false. Every other combination is allowed, including $`a`$ false and $`b`$ true (the rule
says nothing about $`b`$ when $`a`$ is not funded). The row

```math
x_a \le x_b
```

forbids the same combination and nothing else. If $`x_a = 1`$, the row reads $`1 \le x_b`$, so
$`x_b`$ must be 1. If $`x_a = 0`$, it reads $`0 \le x_b`$, which every value of $`x_b`$ satisfies.
That is the parent rule of lesson 1.1.1, $`x_c \le x_{p(c)}`$: "if the child is funded, the parent
is".

So a rule phrased "$`a`$ needs $`b`$", or "$`a`$ only if $`b`$", is "if $`a`$ then $`b`$", and its row
is $`x_a \le x_b`$: the project that needs the other goes on the **small** side of the row. Sources
name the projects in different orders (MIT's 15.053 text, in Further reading, writes its contingent
investment as $`x_j \ge x_i`$ because there $`i`$ is the one that needs $`j`$), so read the sides,
not the letters.

Two more rules come out of it by substituting NOT:

- **"If $`a`$ then not $`b`$"** (not both): $`x_a \le 1 - x_b`$, which is $`x_a + x_b \le 1`$.
- **"If not $`a`$ then $`b`$"** (at least one of the two, the OR of $`a`$ and $`b`$ as a rule):
  $`1 - x_a \le x_b`$, which is $`x_a + x_b \ge 1`$.

A row says what you mean if it allows exactly the 0/1 combinations the logic allows. With two or
three binaries there are only four or eight combinations, so you can check every one. The program
below builds each row in a tiny model, fixes the binaries to each combination through their bounds,
and asks HiGHS whether the model is feasible (the module's `allowed_values` helper); then it
compares the combinations the row allows with those the logic allows:

```python
RULES = [
    # name, variables, the logic, the rows, the rows as text
    ("a -> b", "ab", lambda a, b: (not a) or b,
     lambda m, v: m.add_linear_constraint(v["a"] <= v["b"]), "x_a <= x_b"),
    ("a -> not b", "ab", lambda a, b: not (a and b),
     lambda m, v: m.add_linear_constraint(v["a"] + v["b"] <= 1), "x_a + x_b <= 1"),
```

Each allowed combination prints as its digits in the order `ab` (or `abc`), so `01` means
$`x_a = 0`$ and $`x_b = 1`$:

```text
rule               row                      assignments the row allows         logic
a -> b             x_a <= x_b               00 01 11                           same
a -> not b         x_a + x_b <= 1           00 01 10                           same
not a -> b         x_a + x_b >= 1           01 10 11                           same
```

`a -> b` allows every combination except `10`, which is exactly the forbidden one.

The same row also says something you did not write. "If $`a`$ then $`b`$" is the same rule as "if
not $`b`$ then not $`a`$" (its **contrapositive**), and $`x_a \le x_b`$ enforces both at once: with
$`x_b = 0`$ the row reads $`x_a \le 0`$. So "P028 needs P024" also means "without P024, no P028",
and a planner reading the solution should expect both.

CP-SAT, OR-Tools' constraint solver (lessons 4.4.1 to 4.4.4), does have logic operators. Its Boolean variables
have negations (`~x` reads "not x"), and it takes implications and clauses as constraints of their
own. The OR-Tools sample `reified_sample_sat.py` writes "if $`b`$ then $`x`$ and not $`y`$" three
ways: an AND that applies only when $`b`$ is true, two implications, and two OR clauses.
`cpsat_logic.py` enumerates every solution of each version and puts the two linear rows
$`b \le x`$ and $`b \le 1 - y`$ (over 0/1 variables in MathOpt) beside them, checked with `allowed_values`:

```python
if version == "bool_and":                    # a half-reified bool and
    model.add_bool_and(x, ~y).only_enforce_if(b)
elif version == "implication":               # two implications
    model.add_implication(b, x)
    model.add_implication(b, ~y)
elif version == "bool_or":                   # two clauses
    model.add_bool_or(~b, x)
    model.add_bool_or(~b, ~y)
```

```text
b -> (x and not y); assignments allowed, as b x y:
  bool_and     000 001 010 011 110
  implication  000 001 010 011 110
  bool_or      000 001 010 011 110
  linear rows  000 001 010 011 110
all four the same: True
```

All four allow the same five assignments, and only `110` has $`b`$ at 1. The logic form and the
linear form state one rule. The difference is in who solves it: a MILP solver needs the linear
rows, and CP-SAT accepts either.

## AND or OR on Either Side of an Implication Is Still One Row

Real rules join more than two statements. Three shapes cover almost all of them:

- **"If $`a`$ and $`b`$, then $`c`$."** $`x_a + x_b - 1`$ is 1 when both are funded and 0 or $`-1`$
  otherwise, so the row $`x_a + x_b - 1 \le x_c`$ forces $`x_c = 1`$ only when both are funded.
- **"If $`a`$, then $`b`$ or $`c`$."** $`x_b + x_c`$ is at least 1 when either is funded, so
  $`x_a \le x_b + x_c`$ forces one of them only when $`a`$ is funded.
- **"If $`a`$ or $`b`$, then $`c`$."** This is two implications, $`a \Rightarrow c`$ and
  $`b \Rightarrow c`$, so two rows: $`x_a \le x_c`$ and $`x_b \le x_c`$.

The same truth-table check confirms all three. Its last rule is a classic slip, the implication
written the wrong way round:

```python
("a -> b, reversed", "ab", lambda a, b: (not a) or b,
 lambda m, v: m.add_linear_constraint(v["a"] >= v["b"]), "x_a >= x_b"),
]
```

```text
(a and b) -> c     x_a + x_b - 1 <= x_c     000 001 010 011 100 101 111        same
a -> (b or c)      x_a <= x_b + x_c         000 001 010 011 101 110 111        same
(a or b) -> c      x_a <= x_c, x_b <= x_c   000 001 011 101 111                same
a -> b, reversed   x_a >= x_b               00 10 11                           DIFFERS
```

`(a and b) -> c` refuses only `110`; `a -> (b or c)` refuses only `100`. The reversed row allows
`10` and refuses `01`: it says "if $`b`$ then $`a`$", a different rule that the solver will enforce
without complaint. Read against the rule it was meant to state, "$`a`$ needs $`b`$", the reversed row
lets through the plan that funds $`a`$ without $`b`$ (`10`), which the rule forbids, and refuses the
plan that funds $`b`$ alone (`01`), which the rule allows. No solver can catch a row written the
wrong way round, because both directions are valid rows. A four- or eight-line truth table, or a test that fixes a plan the rule must refuse
and checks that the model refuses it, does catch it.

"If $`a`$ or $`b`$, then $`c`$" can also be written as the single row $`x_a + x_b \le 2\,x_c`$.
It allows the same 0/1 combinations, but its LP relaxation allows more fractional points: with
$`x_a = 1`$, $`x_b = 0`$ it lets $`x_c = 0.5`$, which the two-row form refuses. Lesson 3.1.2 showed
that two correct formulations can have different LP bounds, and the one that admits fewer
fractional points can never have the weaker bound; prefer the two rows.

Now the engineers' rules. Each is one row on GridCap small's selection model:

```python
def conflict(sel):        # P030 and P032 share one Valley line outage: not both
    x = sel.x
    sel.model.add_linear_constraint(x["P030"] + x["P032"] <= 1, name="outage_P030_P032")


def needs(sel):           # the P028 tower replacement needs P024 to carry Ridge load meanwhile
    x = sel.x
    sel.model.add_linear_constraint(x["P028"] <= x["P024"], name="needs_P028_P024")


def both_need(sel):       # P022 and P025 together overload the Valley yard unless P033 rebuilds it
    x = sel.x
    sel.model.add_linear_constraint(x["P022"] + x["P025"] - 1 <= x["P033"], name="yard_P022_P025")


def needs_one(sel):       # undergrounding P034 needs one of the Plains replacements P013 or P040
    x = sel.x
    sel.model.add_linear_constraint(x["P034"] <= x["P013"] + x["P040"], name="feed_P034")
```

The program solves the model with each rule alone, then with all four:

```text
no extra rule: NPV $25,336k, 20 projects
conflict   NPV $24,706k (-630)  adds ['P001', 'P008', 'P012', 'P023', 'P026']  drops ['P002', 'P015', 'P032']
needs      NPV $24,897k (-439)  adds ['P024', 'P026']  drops ['P022', 'P029']
both_need  NPV $25,290k (-46)  adds ['P004', 'P008', 'P012', 'P026']  drops ['P022']
needs_one  NPV $24,991k (-345)  adds ['P004', 'P008', 'P013', 'P026']  drops ['P022', 'P029']
all four   NPV $23,746k (-1,590)  adds ['P008', 'P013', 'P024', 'P036']  drops ['P022', 'P029', 'P032']
```

Read each line against its rule. Under `conflict`, P032 leaves the plan and P030 stays. Under
`needs`, the plan keeps P028 and pays for P024 to do it. Under `both_need`, the solver does not buy
P033 at all: it drops P022, so the "if both" never happens, which the row allows and costs only
$46k. Under `needs_one` the plan buys P013 to keep P034. Each rule is a row the solver satisfies in
whatever way costs least, which is not always the way the engineer pictured.

The rules also interact. Alone they cost $630k, $439k, $46k and $345k, $1,460k in all; together
they cost $1,590k, because the cheapest way around one rule can run into another.

<!-- practice 1 -->

## AND, OR and XOR as Values Need a New Binary, Pinned From Both Sides

So far every piece of logic was a *rule*: a row that refuses plans. Sometimes the model needs the
logic as a *value* instead, a number other rows and the objective can use. "The Valley region gets
distribution work" is the OR of its distribution projects' binaries; a saving that applies "when
both P030 and P032 are funded" needs the AND of two binaries. A value needs a variable: a new binary
$`z`$, with rows that pin it to the logic.

For $`z = a \text{ AND } b`$, the rows are

```math
z \le x_a, \qquad z \le x_b, \qquad z \ge x_a + x_b - 1
```

The first two **push $`z`$ down**: if either project is not funded, $`z`$ must be 0. The third
**pushes $`z`$ up**: if both are funded, $`x_a + x_b - 1 = 1`$ and $`z`$ must be 1. For
$`z = a \text{ OR } b`$:

```math
z \ge x_a, \qquad z \ge x_b, \qquad z \le x_a + x_b
```

the first two push $`z`$ up when either is funded, and the last pushes it down when neither is.
Both extend to any number of projects: an AND of $`n`$ binaries is $`z \le x_i`$ for each $`i`$ and
$`z \ge \sum_i x_i - (n - 1)`$; an OR is $`z \ge x_i`$ for each $`i`$ and $`z \le \sum_i x_i`$.

**XOR** ("exactly one of the two") as a value takes four rows, two each way:

```math
z \ge x_a - x_b, \qquad z \ge x_b - x_a, \qquad z \le x_a + x_b, \qquad z \le 2 - x_a - x_b
```

The program lists, for each combination of $`x_a`$ and $`x_b`$, the values of $`z`$ the rows allow:
with all the rows, with only the rows that push $`z`$ down, and with only those that push it up:

```text
z = a AND b  a b | all rows | 'down' rows only | 'up' rows only
             0 0 | 0        | 0                | 0 1
             0 1 | 0        | 0                | 0 1
             1 0 | 0        | 0                | 0 1
             1 1 | 1        | 0 1              | 1
z = a OR b   a b | all rows | 'down' rows only | 'up' rows only
             0 0 | 0        | 0                | 0 1
             0 1 | 1        | 0 1              | 1
             1 0 | 1        | 0 1              | 1
             1 1 | 1        | 0 1              | 1
z = a XOR b  a b | all rows | 'down' rows only | 'up' rows only
             0 0 | 0        | 0                | 0 1
             0 1 | 1        | 0 1              | 1
             1 0 | 1        | 0 1              | 1
             1 1 | 0        | 0                | 0 1
```

With all the rows, every line has exactly one value of $`z`$, and it is the logic's value: $`z`$
is pinned. With one side only, $`z`$ is pinned on some lines and free on others. The "down" rows
alone leave $`z`$ free to be 0 when the logic says 1; the "up" rows alone leave it free to be 1
when the logic says 0.

XOR as a *rule* is simpler than XOR as a value: "fund exactly one of $`a`$ and $`b`$" is the single
row $`x_a + x_b = 1`$, with no new variable. Use the four rows only when the model needs the XOR's
value somewhere else.

## Pin Only the Side the Model Would Exploit, or Both When Unsure

A variable pinned from one side is not always a bug. The solver moves a free variable in whichever
direction helps the objective, so a side matters only if the solver *wants* to move $`z`$ that way.
The program `one_side.py` shows both cases on GridCap small with $`y_r`$, the OR of region
$`r`$'s distribution projects ("region $`r`$ gets distribution work"):

```python
y = {r: model.add_binary_variable(name=f"y_{r}") for r in REGIONS}
for r in REGIONS:
    if "up" in sides:     # any distribution project in r pushes y[r] up to 1
        for i in members[r]:
            model.add_linear_constraint(y[r] >= x[i], name=f"up_{r}_{i}")
    if "down" in sides:   # no distribution project in r pushes y[r] down to 0
        model.add_linear_constraint(y[r] <= sum(x[i] for i in members[r]), name=f"down_{r}")
```

First, a rule: the distribution engineering team can supervise work in at most 2 regions, so
$`\sum_r y_r \le 2`$. Second, a reward: planners credit $150k of value for every region that gets
distribution work, so the objective gains $`150 \sum_r y_r`$. Each is solved with both sides, with
one side, and with the other:

```text
Rule: distribution work in at most 2 regions
  rows down+up  NPV $25,131k  regions served ['Coast', 'Plains']
  rows up       NPV $25,131k  regions served ['Coast', 'Plains']
  rows down     NPV $25,336k  regions served ['Ridge', 'Coast', 'Plains']
Credit: $150k for each region that gets distribution work
  rows down+up  claims $25,833k for 4 regions; plan serves ['Ridge', 'Valley', 'Coast', 'Plains'], worth $25,833k
  rows down     claims $25,833k for 4 regions; plan serves ['Ridge', 'Valley', 'Coast', 'Plains'], worth $25,833k
  rows up       claims $25,936k for 4 regions; plan serves ['Ridge', 'Coast', 'Plains'], worth $25,786k
```

- **In the rule, the solver wants $`y`$ small**, because every $`y_r`$ at 1 uses up the limit of 2.
  So the "up" rows are the ones that matter: they force $`y_r = 1`$ wherever there is work. With them
  alone the answer is the same as with both. With the "down" rows alone, nothing forces $`y_r`$ up,
  so the solver may leave every $`y_r`$ at 0 and meet the limit on paper: the plan serves 3 regions
  and keeps its old value, $25,336k. The rule is silently gone.
- **In the reward, the solver wants $`y`$ large**, because every $`y_r`$ at 1 adds $150k. So the
  "down" rows matter: they keep $`y_r = 0`$ where there is no work. With the "up" rows alone, the
  solver sets all four to 1 and claims $25,936k while the plan serves only 3 regions; its real
  value is $25,786k. The report would be wrong by $150k, and the plan is not even the best one,
  which is worth $25,833k.

So the side to keep is the one that resists the solver: when $`y`$ is pushed small (a $`\le`$ row
or a cost), keep the rows that push it up; when $`y`$ is pushed large (a $`\ge`$ row or a reward),
keep the rows that push it down. A dropped side saves rows but makes the model depend on how $`y`$
is used, and a later change (a reward added to a variable that was only capped) breaks it without
a sound. When a variable is used in more than one way, or you are unsure, write both sides: the
extra rows never cut off a correct plan.

<!-- practice 2 -->

## The Model

The selection model on GridCap small with this lesson's rows marked. The programs add the four
engineering rules and the region variables in separate runs; together they make this model.

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$
the child projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups; $`R`$ the
regions (Ridge, Valley, Coast, Plains); $`D_r \subseteq P`$ the distribution projects in region
$`r`$.

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ ($k); $`B`$, the capital budget ($38,390k);
$`K = 2`$, the most regions with distribution work.

**Variables.**

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(1 if project } i \text{ is funded)} \\
& y_r \in \{0, 1\} && \forall r \in R && \text{(1 if region } r \text{ gets distribution work)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

(the credit run adds $`150 \sum_{r \in R} y_r`$ to it).

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
x_{P030} + x_{P032} &\le 1 && && \text{(outage\_P030\_P032)} \quad \leftarrow \text{this lesson} \\
x_{P028} &\le x_{P024} && && \text{(needs\_P028\_P024)} \quad \leftarrow \text{this lesson} \\
x_{P022} + x_{P025} - 1 &\le x_{P033} && && \text{(yard\_P022\_P025)} \quad \leftarrow \text{this lesson} \\
x_{P034} &\le x_{P013} + x_{P040} && && \text{(feed\_P034)} \quad \leftarrow \text{this lesson} \\
y_r &\ge x_i && \forall r \in R,\ i \in D_r && \text{(up}_{r,i}) \quad \leftarrow \text{this lesson} \\
y_r &\le \sum_{i \in D_r} x_i && \forall r \in R && \text{(down}_r) \quad \leftarrow \text{this lesson} \\
\sum_{r \in R} y_r &\le K && && \text{(regions)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

| Label | Row name in the programs |
| --- | --- |
| up$`_{r,i}`$, down$`_r`$ | `up_Ridge_P019`, `down_Ridge` |
| the four engineering rules | `outage_P030_P032`, `needs_P028_P024`, `yard_P022_P025`, `feed_P034` |

## Summary

- **NOT is one minus the binary.** $`1 - x_a`$ is the truth value of "not $`a`$" and can stand
  wherever $`x_a`$ can.
- **An implication between two decisions is one inequality.** $`a \Rightarrow b`$ is
  $`x_a \le x_b`$, which also enforces "not $`b`$ implies not $`a`$"; not both is
  $`x_a + x_b \le 1`$, at least one is $`x_a + x_b \ge 1`$.
- **AND or OR on either side of an implication is still one row.** Check a row against its truth
  table; a reversed row is valid and wrong.
- **AND, OR and XOR as values need a new binary, pinned from both sides.** Rows that push $`z`$
  down and rows that push it up together leave exactly the logic's value.
- **Pin only the side the model would exploit, or both when unsure.** A dropped side either
  deletes a rule silently or lets the solver claim value it does not deliver.

## Reference

| Rule in words | Row |
| --- | --- |
| if $`a`$ then $`b`$ | $`x_a \le x_b`$ |
| not both $`a`$ and $`b`$ | $`x_a + x_b \le 1`$ |
| at least one of $`a`$, $`b`$ | $`x_a + x_b \ge 1`$ |
| exactly one of $`a`$, $`b`$ | $`x_a + x_b = 1`$ |
| $`a`$ and $`b`$ together or not at all | $`x_a = x_b`$ |
| if $`a`$ and $`b`$ then $`c`$ | $`x_a + x_b - 1 \le x_c`$ |
| if $`a`$ then $`b`$ or $`c`$ | $`x_a \le x_b + x_c`$ |
| if $`a`$ or $`b`$ then $`c`$ | $`x_a \le x_c`$ and $`x_b \le x_c`$ |

| Value | Rows pushing $`z`$ down | Rows pushing $`z`$ up |
| --- | --- | --- |
| $`z = \text{AND}_i\, x_i`$ ($`n`$ terms) | $`z \le x_i`$ for each $`i`$ | $`z \ge \sum_i x_i - (n-1)`$ |
| $`z = \text{OR}_i\, x_i`$ | $`z \le \sum_i x_i`$ | $`z \ge x_i`$ for each $`i`$ |
| $`z = a \text{ XOR } b`$ | $`z \le x_a + x_b`$, $`z \le 2 - x_a - x_b`$ | $`z \ge x_a - x_b`$, $`z \ge x_b - x_a`$ |

| $`z`$ is used where the solver wants it | Keep the rows that push it |
| --- | --- |
| small (in a $`\le`$ row, or as a cost) | up |
| large (in a $`\ge`$ row, or as a reward) | down |
| both, or you are not sure | both ways |

| CP-SAT | What it states |
| --- | --- |
| `~x` | the negation of Boolean `x`, "not x" |
| `add_implication(a, b)` | if `a` then `b` |
| `add_bool_or(a, b, ...)` | at least one is true |
| `add_bool_and(a, b).only_enforce_if(c)` | if `c` then all of `a`, `b` |

**Further reading:** [CP-SAT sample reified_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/reified_sample_sat.py) (the rule adapted in `cpsat_logic.py`, written as an enforced AND, as implications and as clauses); [CP-SAT sample bool_or_sample_sat.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/sat/samples/bool_or_sample_sat.py) (a clause over a literal and a negated one, with `~y` as another spelling of `y.negated()`); [CP-SAT Solver (OR-Tools)](https://developers.google.com/optimization/cp/cp_solver) (CP-SAT works over the integers only, and lists every solution through a solution callback with `enumerate_all_solutions`, the method `cpsat_logic.py` uses); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.1 writes a contingent investment, one accepted only if another is, as one row between their binaries, the contingent project's binary never above its prerequisite's, and conflicting projects as a multiple-choice row; section 9.2 lists the logical constraints a binary can express).

## Challenges

1. Write "if P021 is funded then neither P036 nor P016 is" as rows. How many rows do you need?
2. "P030 and P032 together or not at all" is $`x_{P030} = x_{P032}`$. Which two implications is it?
3. In `one_side.py`, give the credit only to regions with *transmission* work and run the three
   variants. Predict which one claims too much before you run it.

## Design Note: Test a Logic Row on the Plans It Must Refuse

Every row in this lesson is short, and every one can be written backwards without any tool
noticing: $`x_a \ge x_b`$ is as valid a row as $`x_a \le x_b`$. The cheapest protection is the one
the truth-table program uses: fix a plan the rule must refuse, check the model refuses it, and fix a
plan the rule must allow, check the model allows it. With two or three binaries that covers every
case; on a real model, one allowed and one refused plan per rule catches the reversed row, the
missing side and the wrong project id. Section 12 builds that into a test suite, and this module's
practices are graded exactly that way.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**implications.py.** Checks each implication row against its truth table by fixing the binaries
and asking HiGHS (*An Implication Between Two Decisions Is One Inequality*, *AND or OR on Either
Side*). *Try:* Add the rule "if $`a`$ or $`b`$ then $`c`$" written as $`x_a + x_b \le 2x_c`$.
Predict whether the table says "same".

- Program: [implications.py](src/implications.py)

**gridcap_rules.py.** Adds the four engineering rules to GridCap small's model, one at a time and
together. *Try:* Reverse the `needs` row to `x["P028"] >= x["P024"]`. Predict which projects change.

- Program: [gridcap_rules.py](src/gridcap_rules.py)

**and_or_xor.py.** Lists the values of $`z`$ that the AND, OR and XOR rows allow, with all rows and
with each side alone (*AND, OR and XOR as Values Need a New Binary*). *Try:* Add a third input
$`c`$ to the AND gate. Predict how many rows it needs.

- Program: [and_or_xor.py](src/and_or_xor.py)

**one_side.py.** Solves the region rule and the region credit with both sides, the "up" side only
and the "down" side only (*Pin Only the Side the Model Would Exploit*). *Try:* Make the credit
$500k per region. Predict the claimed value with the "up" rows only.

- Program: [one_side.py](src/one_side.py)

**cpsat_logic.py.** OR-Tools' reified sample: "if b then x and not y" in CP-SAT three ways and as
two linear rows, with every assignment each one allows (*An Implication Between Two Decisions Is One
Inequality*). *Try:* Change the rule to "if b then x or y" with `add_bool_or(~b, x, y)`. Predict how
many assignments it allows, then write the linear row.

- Program: [cpsat_logic.py](src/cpsat_logic.py)
