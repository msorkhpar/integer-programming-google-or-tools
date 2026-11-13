# 4.4.2 Native Logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf`

A MILP states a rule between yes/no decisions as a linear row over binaries. "Fund P030 or P032,
not both" becomes $`x_{030} + x_{032} \le 1`$; "undergrounding P034 needs P013 or P040" becomes
$`x_{034} \le x_{013} + x_{040}`$. Each such row is correct, and each needs a moment of algebra to
write and a truth table to check. A rule that switches a whole linear row on or off needs more: a
**big-M row**, where a constant $`M`$ times a binary loosens the row when the binary is 0. $`M`$ has
to be computed from bounds in the data, at least as large as the most the row could be broken by
when it is switched off; a value too large weakens the model, and can leak through the solver's
tolerance. Section 6 teaches these linear forms in depth (lesson 6.1.2 for logic rows, lesson 6.2.1
for deriving $`M`$, lesson 6.2.2 for what a loose $`M`$ does). This lesson shows each linear row it
needs next to its CP-SAT form, so it does not depend on them.

CP-SAT was built for this kind of rule. It has constraints that *are* logic (an OR, an AND, an
implication), and any linear row can be switched on by a truth value with no big-M at all. This
lesson rewrites GridCap's bundle rules with them: parents, alternatives, the engineers' four rules
and an all-or-nothing bundle. It is the same model as lesson 4.4.1; only the way the rules are
written changes.

GridCap is a fictional utility's portfolio, generated for this course; the rules are invented for
the course.

## The Model

Lesson 4.4.1's model, with every logic rule written as logic. With the sets, parameters and
variables of lesson 4.4.1 ($`x_i \in \{0, 1\}`$ funds project $`i`$, $`k \in \{0, \dots, 4\}`$ counts
tranches):

```math
\max \; \sum_{i \in P} v_i\, x_i \;-\; 300\, k
```

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B + 500\, k && && \text{(budget)} \\
\sum_{i \in P_g} n_i\, x_i &\le N_g && \forall g \in G && \text{(crews}_g) \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\Rightarrow x_{p(c)} && \forall c \in C && \text{(parent}_c) \quad \leftarrow \text{now an implication} \\
\textstyle\text{AtMostOne}(x_i : i \in a) & && \forall a \in \mathcal{A} && \text{(alt}_a) \quad \leftarrow \text{now at-most-one} \\
\lnot x_{030} \lor \lnot x_{032} & && && \text{(conflict)} \\
x_{028} &\Rightarrow x_{024} && && \text{(needs)} \\
\lnot x_{022} \lor \lnot x_{025} \lor x_{033} & && && \text{(both\_need)} \\
x_{034} &\Rightarrow (x_{013} \lor x_{040}) && && \text{(needs\_one)} \\
x_{019} &= x_{024} && && \text{(bundle)}
\end{aligned}
```

$`\lnot`$ is NOT, $`\lor`$ is OR and $`\Rightarrow`$ is "implies" (if the left is true, the right
must be). The last five rows are four rules from GridCap's engineers (lesson 6.1.2, in
section 6, writes the same four as linear rows) and one new rule, an
**all-or-nothing bundle**: P019 and P024, two Ridge distribution jobs that share one substation
design, are funded together or not at all. Each row maps to one CP-SAT call:

| Label | CP-SAT |
| --- | --- |
| parent$`_c`$ | `add_implication(x[c], x[p])` |
| alt$`_a`$ | `add_at_most_one(x[i] for i in a)` |
| conflict | `add_at_most_one(x["P030"], x["P032"])` |
| needs | `add_implication(x["P028"], x["P024"])` |
| both_need | `add_bool_or(~x["P022"], ~x["P025"], x["P033"])` |
| needs_one | `add_bool_or(x["P013"], x["P040"]).only_enforce_if(x["P034"])` |
| bundle | `add(x["P019"] == x["P024"])` |

## A Literal Is a Boolean Variable or Its Negation

CP-SAT's logic constraints take **literals**. A literal is a Boolean variable `x`, or its negation
`~x` ("not x"), which is true exactly when `x` is false. You never create `~x`: the `~` operator gives
it, and `~~x` is `x` again. The OR-Tools example on literals shows just that, adapted here:

```python
model = cp_model.CpModel()
x = model.new_bool_var("x")
not_x = ~x
print(x, not_x, ~not_x)
```

```text
x not(x) x
```

A MILP writes "not funded" as $`1 - x_a`$, an expression. CP-SAT's `~x` is not an expression to
be moved around a row; it is a truth value the logic constraints read directly, and it costs nothing.
Older code writes it `x.Not()`; OR-Tools 9.15 accepts both, and its examples use `~x`.

A rule can be said in several ways, and CP-SAT accepts each. The OR-Tools example on reified
constraints writes "if b, then x and not y" three times: as an AND switched on by `b`, as two
implications, and as two ORs. The truth-table helper of this module fixes the three Booleans to each
of their 8 combinations and asks CP-SAT whether the constraints still hold:

```python
def with_bool_and(model, v):
    model.add_bool_and(v["x"], ~v["y"]).only_enforce_if(v["b"])


def with_implications(model, v):
    model.add_implication(v["b"], v["x"])
    model.add_implication(v["b"], ~v["y"])


def with_bool_or(model, v):
    model.add_bool_or(~v["b"], v["x"])
    model.add_bool_or(~v["b"], ~v["y"])
```

```text
with_bool_and      b x y allowed: 000 001 010 011 110
with_implications  b x y allowed: 000 001 010 011 110
with_bool_or       b x y allowed: 000 001 010 011 110
```

Each combination prints as its digits in the order `bxy`, so `110` means $`b = 1, x = 1, y = 0`$.
All three allow the same five: every combination with $`b = 0`$, and with $`b = 1`$ only
$`x = 1, y = 0`$. So "if b then x" is the same rule as "not b, or x", and you can write whichever reads
best.

## Each Logic Constraint Allows Exactly the Assignments Its Name Says

CP-SAT's logic constraints, from the `cp_model.py` docstrings, each checked with the truth-table
helper:

```text
constraint                             allows
add_bool_or(a, b)                      01 10 11
add_bool_and(a, ~b)                    10
add_implication(a, b)                  00 01 11
add_at_most_one(a, b, c)               000 001 010 100
add_exactly_one(a, b, c)               001 010 100
add_bool_xor(a, b)                     01 10
add_bool_or(~a, ~b, c)                 000 001 010 011 100 101 111
add_bool_or(b, c).only_enforce_if(a)   000 001 010 011 101 110 111
add(a == b)                            00 11
```

| Constraint | Means | The linear row of a MILP |
| --- | --- | --- |
| `add_bool_or(l1, l2, ...)` | at least one literal is true (a **clause**) | $`x_a + x_b \ge 1`$ |
| `add_bool_and(l1, l2, ...)` | every literal is true | each $`x = 1`$ |
| `add_implication(a, b)` | if `a` then `b` | $`x_a \le x_b`$ |
| `add_at_most_one(...)` | at most one is true | $`\sum x \le 1`$ |
| `add_exactly_one(...)` | exactly one is true | $`\sum x = 1`$ |
| `add_bool_xor(l1, l2, ...)` | an odd number are true | needs extra variables |
| `add(a == b)` | the two are equal | $`x_a = x_b`$ |

Read the table against the linear rows. `add_implication(a, b)` refuses only `10` ("a without b"), as
$`x_a \le x_b`$ did. `add_bool_or(~a, ~b, c)` refuses only `110`: it is "if a and b, then c", because
"a and b imply c" is false only when a and b are true and c is false, and so is the clause "not a, or
not b, or c". The only constraint here without a short linear row is XOR; its docstring also says it
does not support `only_enforce_if`, the switch the next sections use.

**A clause** is an OR of literals. Every rule about yes/no decisions can be written as clauses, and
clauses are what the SAT part of CP-SAT works with best (the Primer's *Basic Modeling* chapter says
short `add_bool_or` clauses are efficient). That is the practical reason to write logic as logic:
the solver receives the rule in the form it reasons with, instead of a row it has to recognise.

## GridCap's Rules Become One Constraint Each, With No Big-M

The lesson's model on GridCap small, first with no extra rule, then with each rule alone, then with
all five. Each rule is written once in CP-SAT and once as the linear row of the table above, and
HiGHS solves the linear version through MathOpt:

```python
RULES = [
    ("conflict", lambda m, x: m.add_at_most_one(x["P030"], x["P032"]),
     lambda m, x: m.add_linear_constraint(x["P030"] + x["P032"] <= 1)),
    ("needs", lambda m, x: m.add_implication(x["P028"], x["P024"]),
     lambda m, x: m.add_linear_constraint(x["P028"] <= x["P024"])),
    ("both_need", lambda m, x: m.add_bool_or(~x["P022"], ~x["P025"], x["P033"]),
     lambda m, x: m.add_linear_constraint(x["P022"] + x["P025"] - 1 <= x["P033"])),
    ("needs_one", lambda m, x: m.add_bool_or(x["P013"], x["P040"]).only_enforce_if(x["P034"]),
     lambda m, x: m.add_linear_constraint(x["P034"] <= x["P013"] + x["P040"])),
    ("bundle", lambda m, x: m.add(x["P019"] == x["P024"]),
     lambda m, x: m.add_linear_constraint(x["P019"] == x["P024"])),
]
```

```text
no extra rule  OPTIMAL  objective 25,374
conflict       OPTIMAL  objective 24,706 (-668)  HiGHS 24,706  adds ['P001', 'P012', 'P014', 'P023']  drops ['P002', 'P015', 'P032']
needs          OPTIMAL  objective 24,899 (-475)  HiGHS 24,899  adds ['P014', 'P024']  drops ['P008', 'P022']
both_need      OPTIMAL  objective 25,124 (-250)  HiGHS 25,124  adds ['P001', 'P014']  drops ['P002', 'P008', 'P022']
needs_one      OPTIMAL  objective 24,982 (-392)  HiGHS 24,982  adds ['P013']  drops ['P022']
bundle         OPTIMAL  objective 25,131 (-243)  HiGHS 25,131  adds ['P012', 'P014']  drops ['P008', 'P019']
all five       OPTIMAL  objective 23,775 (-1,599)  HiGHS 23,775  adds ['P013', 'P014', 'P024', 'P036']  drops ['P011', 'P022', 'P029', 'P032']
```

On every line CP-SAT and HiGHS agree on the value, so the logic constraint and the linear row allow
the same plans, as the truth tables said they would. (Lesson 6.1.2, in section 6, solves the same
rules on a model without the crew rows and the credit line, so its numbers differ from these.)

The parent and alternative rules are now native too: `selection(small, native=True)` writes them as
`add_implication` and `add_at_most_one`, and lesson 4.4.1's linear version reaches the same optimum,
$25,374k (the module's tests check it).

Read each line against its rule. Under `bundle`, the plan had P019 without
P024, and the cheapest repair is to drop P019 (and P008) rather than add P024. Under `both_need`, the
solver drops P022 rather than buying P033, so the "if both" never happens. A logic constraint, like a
row, is satisfied in whatever way costs least.

None of these rules needed a big-M, and none needs one as a linear row either: a rule among yes/no
decisions is a row or two with no $`M`$, as the table above shows. What CP-SAT changes here is the writing and the
reading. `add_bool_or(x["P013"], x["P040"]).only_enforce_if(x["P034"])` says the engineer's sentence
in the engineer's order, and a reviewer checks it without redoing the algebra. Where CP-SAT removes
the big-M is the next section: a *linear* row switched by a decision.

<!-- practice 1 -->

## OnlyEnforceIf Switches a Linear Row On a Conjunction of Literals

`only_enforce_if(l1, l2, ...)` can follow any constraint that supports it (linear rows, `add_bool_or`,
`add_bool_and` and most others; not `add_bool_xor`). The constraint then holds when *every* listed
literal is true, and is ignored otherwise. The listed literals are its **enforcement literals**.
Here it is in three shapes on GridCap small (lesson 6.2.3, in section 6, sets it beside MathOpt's
indicator constraints):

```python
rest = sum(capex[i] * x[i] for i in valley_rest)
sel.model.add(rest <= 4_000).only_enforce_if(x["P032"])
```

```python
others = sum(x[i] for i in transmission if i not in ("P017", "P028"))
sel.model.add(others <= 4).only_enforce_if(x["P017"], x["P028"])
```

```python
fee = sel.model.new_bool_var("office_fee")
veg = sum(capex[i] * x[i] for i in vegetation)
sel.model.add(veg <= 2_000).only_enforce_if(~fee)
sel.model.maximize(sum(p.value * x[p.project_id] for p in small.projects) - 300 * sel.k - 150 * fee)
```

```text
P032 caps Valley   OPTIMAL  objective 24,706  P032 funded False  rest of Valley $11,870k
  a big-M row would need M = 11,850
P017 and P028      OPTIMAL  objective 25,158  both funded True  other transmission 4
vegetation fee     OPTIMAL  objective 25,363  vegetation $1,800k  fee False
```

1. **One literal.** "If P032 (the Valley line rebuild) is funded, the rest of Valley's capex stays
   within $4,000k", because the outage leaves the region's construction managers no time for more.
   The optimum drops P032 and keeps $11,870k of other Valley work, worth more than P032. As a big-M
   row this would be $`\text{rest} \le 4{,}000 + M(1 - x_{032})`$, with $`M`$ at least the largest
   value the rest of Valley can reach minus 4,000, $11,850k: when $`x_{032} = 0`$ the row must allow
every value the rest can take (lesson 6.2.1, in section 6, derives such bounds in depth). In CP-SAT
   there is no $`M`$ to compute, to keep up to date when the data changes, or to get wrong.
2. **A conjunction.** "If P017 and P028 are both funded, at most 4 other transmission projects."
   Passing two literals means *both*: the row holds when P017 *and* P028 are funded. (Two copies of
   the row, one enforced by each literal, would mean something else: each copy holds when its own
   literal is true, so the row would hold whenever *either* project is funded.) The optimum
   funds both and keeps exactly 4 others. A MILP would need a big-M times
   $`(2 - x_{017} - x_{028})`$, or first a new binary that linear rows force to be 1 exactly when both
are (lesson 6.1.2, in section 6, writes such an AND).
3. **A negated literal.** "A $150k program-office fee applies when vegetation capex passes $2,000k."
   The fee is a Boolean `fee`, and the row "vegetation capex at most $2,000k" is enforced when the
   fee is *not* paid: `only_enforce_if(~fee)`. The optimum trims vegetation to $1,800k and pays no
   fee. The plan before had $2,260k of vegetation; it would now pay the fee and be worth
   $25,374k − $150k = $25,224k, less than the $25,363k of the trimmed plan.

The rule to remember: `only_enforce_if` means "if", not "if and only if". When its literals are false
the row is simply not checked, and nothing forces it to be false. That is enough here, and the next
section shows when it is not.

<!-- practice 2 -->

## Write the Side the Objective Would Exploit, or Both

An enforced row is **half-reified**: the literal implies the row, and nothing goes the other way. A
**reified** constraint, an "if and only if", is two half-reified ones: the literal implies the row,
and its negation implies the row's opposite. The OR-Tools guide on channeling builds one this way, a
Boolean `b` that is true exactly when $`x \ge 5`$:
`model.add(x >= 5).only_enforce_if(b)` and `model.add(x < 5).only_enforce_if(~b)`.

When is one side enough? When the objective only ever pushes the literal one way, and that way is
the side you wrote. The fee above is a cost, so the solver wants `fee` false; the row enforced on
`~fee` stops it from being false when spending is high. The other direction (fee true while spending
is low) is allowed but never chosen, because it only costs money.

Turn the fee into a $100k **rebate** that the vegetation program earns when its capex *passes*
$2,500k, and the same pattern breaks. The solver now wants `rebate` true:

```python
for side in ("veg <= 2500 if not rebate", "veg >= 2501 if rebate"):
    sel = selection(small, native=True)
    x = sel.x
    rebate = sel.model.new_bool_var("rebate")
    veg = sum(capex[i] * x[i] for i in vegetation)
    if side.endswith("not rebate"):
        sel.model.add(veg <= 2_500).only_enforce_if(~rebate)
    else:
        sel.model.add(veg >= 2_501).only_enforce_if(rebate)
```

```text
rebate, veg <= 2500 if not rebate  OPTIMAL  objective 25,474  vegetation $2,260k  rebate True
rebate, veg >= 2501 if rebate      OPTIMAL  objective 25,458  vegetation $2,740k  rebate True
```

The first model claims the rebate with only $2,260k of vegetation work. Its row says "no rebate
implies at most $2,500k", which says nothing about a rebate with little spending, and the solver took
the $100k. The second model writes the side the objective would exploit, "rebate implies more than
$2,500k", and the solver earns the rebate honestly: it raises vegetation to $2,740k, and the plan is
worth $25,458k, $84k more than without a rebate. Both models are `OPTIMAL`; only the first is wrong.
No solver status catches a half-reification written on the wrong side.

When the Boolean is a flag that the objective does not drive, or drives both ways in different
scenarios, write both sides. With both rows, the flag tells the truth whichever way the objective
pulls it:

```python
sel.model.add(veg >= 2_501).only_enforce_if(big)
sel.model.add(veg <= 2_500).only_enforce_if(~big)
```

```text
flag, both sides, pull +100  OPTIMAL  vegetation $2,740k  flag True  truthful True
flag, both sides, pull -100  OPTIMAL  vegetation $2,260k  flag False  truthful True
```

`veg >= 2_501` and `veg <= 2_500` are exact opposites because capex is in whole $k; in CP-SAT that is
always true of a row (every value is an integer), so the opposite of $`\text{expr} \le T`$ is
$`\text{expr} \ge T + 1`$. The rule, "pin only the side the model would exploit, or both when
unsure", holds for linear rows too (lesson 6.1.2, in section 6, applies it); here there is no big-M
on either side.

<!-- practice 3 -->

## Summary

- **A literal is a Boolean variable or its negation.** `~x` is free, and every logic constraint takes
  literals.
- **Each logic constraint allows exactly the assignments its name says.** `add_bool_or`,
  `add_bool_and`, `add_implication`, `add_at_most_one`, `add_exactly_one`, `add_bool_xor` and
  `add(a == b)`; a truth table checks any of them.
- **GridCap's rules become one constraint each, with no big-M.** CP-SAT and HiGHS agree on every
  rule's optimum; the logic version says the rule in its own words.
- **OnlyEnforceIf switches a linear row on a conjunction of literals.** No $`M`$ to compute; several
  literals mean all of them.
- **Write the side the objective would exploit, or both.** `only_enforce_if` is "if", not "if and
  only if"; for a flag, write both rows.

## Reference

| Rule in words | CP-SAT | Linear row of a MILP |
| --- | --- | --- |
| at least one of a, b | `add_bool_or(a, b)` | $`x_a + x_b \ge 1`$ |
| not both a and b | `add_at_most_one(a, b)` or `add_bool_or(~a, ~b)` | $`x_a + x_b \le 1`$ |
| if a then b | `add_implication(a, b)` | $`x_a \le x_b`$ |
| if a and b then c | `add_bool_or(~a, ~b, c)` | $`x_a + x_b - 1 \le x_c`$ |
| if a then b or c | `add_bool_or(b, c).only_enforce_if(a)` | $`x_a \le x_b + x_c`$ |
| a and b together or not at all | `add(a == b)` | $`x_a = x_b`$ |
| if a, then a linear row | `add(row).only_enforce_if(a)` | a big-M row |
| b exactly when a row holds | `add(row).only_enforce_if(b)` and `add(opposite).only_enforce_if(~b)` | two big-M rows |

| Term | Meaning |
| --- | --- |
| literal | a Boolean variable `x` or its negation `~x` |
| clause | an OR of literals, `add_bool_or` |
| enforcement literal | a literal in `only_enforce_if`; the constraint holds when all of them are true |
| half-reified | the literal implies the constraint, and nothing more |
| reified | the literal is true exactly when the constraint holds (two half-reified constraints) |

**Further reading:** [Channeling Constraints (OR-Tools)](https://developers.google.com/optimization/cp/channeling)
(half-reified constraints with `only_enforce_if` and `~b`, and the $`x \ge 5`$ example quoted above);
[CP-SAT samples: `literal_sample_sat.py` and `reified_sample_sat.py` (OR-Tools on GitHub)](https://github.com/google/or-tools/tree/stable/ortools/sat/samples)
(the literal and the three forms of one rule adapted above); [`cp_model.py` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/python/cp_model.py)
(the docstrings of `add_bool_or`, `add_bool_and`, `add_implication`, `add_at_most_one`,
`add_exactly_one`, and `add_bool_xor`'s note that it does not support enforcement);
[`cp_model.proto` (OR-Tools on GitHub)](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto)
(an enforced constraint holds when all its enforcement literals are true, and is ignored otherwise);
[The CP-SAT Primer, Basic Modeling (Krupke)](https://d-krupke.github.io/cpsat-primer/modelling.html)
(logical and conditional constraints, and why `only_enforce_if` usually beats a big-M in CP-SAT).

## Challenges

1. Write `needs_one` as an implication from P034 to a new Boolean "P013 or P040", with that Boolean
   defined by `add_bool_or` and `only_enforce_if`. How many constraints did that take, and do the truth
   tables still match?
2. Remove the parent rule's `add_implication` and write it as `add_bool_or(~x[c], x[p])`. Predict the
   objective.
3. The engineers add "P030 and P032 both need the Valley line out; if both are funded, they must be in
   different years". The model is one-period. What would the model need before it could state that?

## Design Note: Name the Rule, Then Pick Its Form

`engineers_rules.py` keeps each rule as a name with two forms side by side, the CP-SAT constraint and
the MathOpt row. Writing rules as data like this keeps the business sentence next to its code, lets a
test run each rule alone, and makes porting between solvers a matter of adding a column. When a
model's rules come from people who are not modelers, keep their sentence as the rule's comment and
its name as the constraint's name (`with_name`), so a planner reading an infeasibility report later
(lesson 4.6.2) sees words they wrote.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**literals.py.** A literal and its negation, and one rule written three ways, adapted from the OR-Tools
examples `literal_sample_sat.py` and `reified_sample_sat.py` (*A Literal Is a Boolean Variable or Its
Negation*). *Try:* Add a fourth form, `add_bool_and(v["x"], ~v["y"])` with no enforcement literal.
Predict which combinations it allows.

- Program: [literals.py](src/literals.py)

**logic_table.py.** Each logic constraint and the 0/1 assignments it allows (*Each Logic Constraint
Allows Exactly the Assignments Its Name Says*). *Try:* Add `add_bool_xor(a, b, c)`. Predict its four
allowed combinations.

- Program: [logic_table.py](src/logic_table.py)

**engineers_rules.py.** The engineers' rules and the bundle on GridCap small, in CP-SAT and as linear
rows for HiGHS (*GridCap's Rules Become One Constraint Each, With No Big-M*). *Try:* Write the bundle
as two implications instead of `==`. Predict the objective.

- Program: [engineers_rules.py](src/engineers_rules.py)

**enforce_if.py.** Rows switched by one literal, by two, and by a negated one; then the rebate written
on the wrong side and the right one, and a flag with both sides (*OnlyEnforceIf Switches a Linear Row
On a Conjunction of Literals*, *Write the Side the Objective Would Exploit, or Both*). *Try:* Make the
rebate $300k. Predict the vegetation capex of the second model.

- Program: [enforce_if.py](src/enforce_if.py)
