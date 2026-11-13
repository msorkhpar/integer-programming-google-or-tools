# 3.1.3 Why MILP Is Hard: Combinatorial Growth in Numbers

GridCap's IT lead has a capacity question before the planning tool goes to the medium portfolio:
"The small model solved instantly. Medium has ten times the projects. Will it take ten times as
long? A hundred? Should we buy a bigger server?" Lesson 1.1.1 showed that brute force doubles with
every project. This lesson puts numbers on the rest of the story: how many plans there really are,
how a search with a bound avoids almost all of them, and why the size of a model is a poor guide to
how hard it is, in five rules.

GridCap is a fictional utility's portfolio, generated for this course. None of its numbers describe
a real company.

## Plans Double With Every Project, and the Rules Thin Them but Do Not Tame Them

Each yes/no decision has two values, so $`n`$ binaries have
$`2 \times 2 \times \dots \times 2 = 2^n`$ combinations: every project added doubles the count. Lesson 1.1.1 turned that into years of
brute force. A fair objection is that most combinations break a rule, so perhaps the plans worth
checking are few. Count them:

```text
tiny:     256 plans, 32 allowed
small:    2^40 = 1.10e+12 plans, at least 8.94e+08 allowed (30 free projects, 30,760 left after must-dos)
medium:   2^400 = 2.58e+120 plans, at least 2.56e+92 allowed (307 free projects, 311,560 left after must-dos)
```

On tiny every one of the 256 combinations was checked with `broken_rows` (lesson 3.1.1), and 32 keep
every rule: the rules removed seven in eight. On small and medium, checking every combination is
out of the question, so the program counts a part of them it can count exactly. A **free project**
is one that no rule but the budget touches: not must-do, without a parent, in no alternative group.
Fund the must-dos, spend the rest of the budget on any set of free projects that fits, fund nothing
else, and every rule holds. So the number of such sets is a **lower bound** on the number of allowed
plans; the true number is larger.

Even this lower bound is enormous: almost 900 million allowed plans on small, and on medium a
number with 93 digits. (`2.56e+92` is scientific notation: 2.56 times ten to the power 92.) The
rules thin the plans by a large factor, but a large factor of $`2^{400}`$ is still astronomically
many. No rule set that leaves planners real choices makes enumeration practical.

<!-- practice 1 -->

## A Table Over Budget Amounts Counts Plans Without Listing Them

How did the program count 900 million plans without listing them? It never looks at a plan. It
keeps a table, `ways`, with one entry for every budget amount from 0 to $`B`$: `ways[b]` is the
number of sets of the projects seen so far that cost exactly $`b`$.

```python
ways = [1] + [0] * budget                           # one way to spend nothing: the empty plan
yield ways
for c in costs:
    for b in range(budget, c - 1, -1):              # downward, so each project is used at most once
        ways[b] += ways[b - c]
    yield ways
```

Before any project, only $0 can be spent, in one way: the empty plan. Then each project of cost
$`c`$ is added in turn. Every set that costs $`b`$ either leaves the new project out (there are
`ways[b]` of those, already counted) or includes it, and then the rest costs $`b - c`$ (there are
`ways[b - c]` of those). So `ways[b] += ways[b - c]`. The loop runs downward over $`b`$ so that
`ways[b - c]` still holds the count from *before* this project; running upward would let a project
join a set that already contains it. On three projects costing 2, 3 and 4 with a budget of 6:

```text
costs (2, 3, 4), budget 6: ways[0..6] after each project
  after 0 projects: [1, 0, 0, 0, 0, 0, 0]  total 1
  after 1 projects: [1, 0, 1, 0, 0, 0, 0]  total 2
  after 2 projects: [1, 0, 1, 1, 0, 1, 0]  total 4
  after 3 projects: [1, 0, 1, 1, 1, 1, 1]  total 6
```

The six plans are $`\{\}, \{2\}, \{3\}, \{4\}, \{2,3\}, \{2,4\}`$; $`\{3, 4\}`$ costs 7 and is out.
The answer is the sum of the last row. GridCap's costs are all multiples of $10k, so the program
divides every cost and the budget by their greatest common divisor first, which makes the table
ten times shorter.

This method is called **dynamic programming**: build the answer for many sub-budgets from answers
already computed. Its work is one step per project per budget amount, $`n \times B`$ steps, about
9.6 million for medium's 307 free projects and 31,156 budget steps. That is fast here, and it is
not a way around the exponential growth of the next rule. $`B`$ is a *number*, and the work grows
with its size, not with the number of digits it takes to write it down. A budget written in
dollars instead of $10k units makes the table ten thousand times longer; costs with cents make it
longer again. An algorithm whose work grows with the size of the numbers in its input, rather
than with their digits, is called **pseudo-polynomial**. The same table can also find the *best*
plan under one budget, but it breaks down once the model has two budgets (the table needs one axis
per budget) or many other rows.

<!-- practice 2 -->

## Exponential Growth Outruns Every Polynomial

An algorithm's **running time** is how its work grows with the size of its input, $`n`$. When the
work grows like a fixed power of $`n`$, such as $`n^2`$ or $`n^3`$, it is **polynomial**; when it
grows like $`2^n`$, it is **exponential**. The difference is not a constant factor:

```text
    n         n^2         n^3         2^n
   10    1.00e+02    1.00e+03    1.02e+03
   20    4.00e+02    8.00e+03    1.05e+06
   40    1.60e+03    6.40e+04    1.10e+12
  100    1.00e+04    1.00e+06    1.27e+30
  400    1.60e+05    6.40e+07   2.58e+120
```

At $`n = 10`$, $`n^3`$ and $`2^n`$ are about equal. At $`n = 400`$, $`n^3`$ is 64 million, a fraction
of a second for a computer, and $`2^n`$ has 121 digits. Doubling $`n`$ multiplies $`n^3`$ by 8; it
*squares* $`2^n`$.

This is the heart of "why MILP is hard". Linear programs can be solved in polynomial time: there
are algorithms (the interior point methods of lesson 2.4.1)
whose work is bounded by a polynomial in the model's size for every LP. For integer programs, no
such algorithm is known. Computer science classifies the 0/1 knapsack and integer programming in
general as **NP-hard**: a polynomial-time method for them would also give one for a large family
of problems that have resisted every attempt for decades, and most researchers believe none
exists. So no MILP solver can promise to finish every model of 400 binaries quickly.

That is a statement about the worst case. It does not say GridCap medium is slow, and the next two
rules show why it is not.

## A Search Tree With a Bound Visits a Sliver of the Plans

Picture the plans as a tree. The top node has decided nothing. Its two children decide the first
project: fund it, or not. Each of theirs decides the second, and so on; after $`n`$ levels each of
the $`2^n`$ bottom nodes is one complete plan, and the tree has $`2^{n+1} - 1`$ nodes in all. Brute
force visits every node.

A search can skip a node, and everything below it, when it can prove nothing below it beats the
best plan found so far. Lesson 3.1.2 provides the proof: the LP bound of the projects not yet
decided, computed by hand, is a ceiling on any completion of the node. If the value so far plus
that ceiling is no more than the best plan already found, the whole subtree is skipped:

```python
if prune and value + lp_bound(items[k:], room) <= best:
    return                                       # nothing below this node can beat the best plan
cost, worth = items[k]
if cost <= room:
    visit(k + 1, room - cost, value + worth)
visit(k + 1, room, value)
```

The program counts the nodes visited on the first $`n`$ projects of GridCap medium with a budget of
half their cost, three ways: the full tree, a search that only skips projects that do not fit, and
the search with the bound:

```text
nodes visited, first n projects of GridCap medium, budget half their cost:
   n  full tree  budget only  with bound
  10      2,047        1,264          20
  15     65,535       36,462          63
  20  2,097,151    1,137,494         114
  25 67,108,863   36,088,515         106
 100    2.5e+30            -       1,342
 400   5.2e+120            -       5,862
```

The budget check alone saves about half. The bound saves almost everything: 114 nodes instead of
two million at $`n = 20`$, and 5,862 nodes for all 400 projects, against a tree with 121 digits.
(The budget-only search is not run beyond 25 projects: its count roughly doubles with each
project, from 1.1 million at 20 to 36 million at 25.) This search is the core of
**branch-and-bound**, the method MILP solvers such as HiGHS are built on; lessons 3.2.1 to 3.2.4 build it properly, and this lesson only counts its nodes.

## Size Does Not Decide Difficulty; the Bound's Strength Does

The bound did the work above because GridCap's projects differ in value per dollar, so the LP
ceiling quickly shows that most branches cannot win. Give the same search the same costs but make
every project worth exactly its cost, so all ratios are equal, and use a budget no plan can spend
exactly:

```text
same costs, every item worth exactly its cost:
  10      2,047                      218
  15     65,535                   10,195
  20  2,097,151                  448,273
  25 67,108,863               16,782,410
```

Same sizes, same costs, and the search now visits 16.8 million nodes at $`n = 25`$ instead of 106.
With equal ratios the ceiling at a node is roughly "everything that is left fills the budget", which
is almost always above the best plan, so nothing is skipped. The difficulty is in the data, not the
count of variables.

A real solver shows the same thing. HiGHS reports how many nodes its search explored in
`result.solve_stats.node_count`. Compare GridCap's selection with an invented puzzle, not GridCap
data: pick projects so that each of several spend columns comes to *exactly* half its total. Each
column is one equality row:

```python
spend = [[rng.randint(0, 99) for _ in range(n)] for _ in range(rows)]
model = mathopt.Model(name="exact split")
x = [model.add_binary_variable(name=f"x_{j}") for j in range(n)]
for r, row in enumerate(spend):
    model.add_linear_constraint(sum(a * v for a, v in zip(row, x)) == sum(row) // 2, name=f"half_{r}")
```

Both kinds of model were given a limit of 100,000 nodes:

```text
GridCap small selection     40 binaries  OPTIMAL                  1 nodes
GridCap medium selection   400 binaries  OPTIMAL                  1 nodes
exact split, 2 rows         10 binaries  INFEASIBLE              20 nodes
exact split, 3 rows         20 binaries  INFEASIBLE           3,584 nodes
exact split, 4 rows         30 binaries  NO_SOLUTION_FOUND  100,000 nodes (stopped: NODE limit)
```

GridCap medium, 400 binaries, is solved at the first node: its LP bound is within 0.006% of the
best plan (lesson 3.1.2), and HiGHS closed that last sliver without branching at all. Lessons 3.3.1
to 3.3.3 show the techniques solvers use at a node for that: cuts, presolve and heuristics. The split puzzle with 30 binaries and 4 rows explored
100,000 nodes and stopped with neither a plan nor a proof that none exists. `INFEASIBLE` on the
smaller puzzles is a proof that no exact split exists, and proving it took 20 and then 3,584 nodes.

Size is a poor guide in the other direction too. The OR-Tools "MIP with arrays" example of lesson
3.1.1 has only five integer variables, and neither solver proves its optimum at the first node
(`mip_arrays.py` prints both counts):

```text
nodes to prove the optimum:
  HiGHS 9, SCIP 5
```

The OR-Tools page reports 13 branch-and-bound nodes for its own run, with SCIP through the older
linear solver wrapper. Three runs, three counts: a node count belongs to one solver, version and
setting, not to the model, which is one more reason to measure rather than predict.

Why is the puzzle so hard? Its LP relaxation is nearly useless. Setting every $`x_j`$ to 0.5 puts
each row at half its total, within half a unit of its target, and a small shift in one variable
closes that. So the relaxation is satisfied easily at almost every node, and
the bound rules out almost nothing until most variables are fixed. The puzzle has no objective, so
there is no value bound to prune with either. That is the pattern to remember: a MILP is hard when
its LP relaxation is weak, and size matters much less.

So the answer for the IT lead: model size alone does not predict solve time. Measure on realistic
instances (section 11 does it on GridCap large), and keep the formulation strong (section 6), because
the bound is what makes the search short.

## The Model

Two models appear in this lesson. The first is GridCap's selection model of lesson 3.1.1, solved
in the last rule; every count in this lesson is a count of its plans or of its search.

**Sets.** $`P`$ the projects; $`M \subseteq P`$ must-do; $`C \subseteq P`$ children with parent
$`p(c)`$; $`\mathcal{G}`$ alternative groups. **Parameters.** $`\text{capex}_i`$, $`\text{npv}_i`$
($k); $`B`$, the capital budget ($k). **Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$.

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{npv}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{capex}_i\, x_i \le B && && \text{(budget)} \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
& \sum_{i \in g} x_i \le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
& x_i \in \{0, 1\} && \forall i \in P
\end{aligned}
```

The second is the invented exact-split puzzle. **Sets.** $`J`$ the items, $`R`$ the spend columns.
**Parameters.** $`a_{r,j}`$, the spend of item $`j`$ in column $`r`$ (whole numbers from 0 to 99).
**Variables.** $`x_j \in \{0, 1\}`$: item $`j`$ is picked. **Objective.** None: any plan that keeps
the rows will do (a **feasibility problem**). **Constraints.**

```math
\begin{aligned}
\sum_{j \in J} a_{r,j}\, x_j &= \Big\lfloor \tfrac{1}{2} \sum_{j \in J} a_{r,j} \Big\rfloor && \forall r \in R && \text{(half}_r) \\
x_j &\in \{0, 1\} && \forall j \in J
\end{aligned}
```

## Summary

- **Plans double with every project, and the rules thin them but do not tame them.** GridCap small
  has at least 8.94e+08 allowed plans and medium at least 2.56e+92.
- **A table over budget amounts counts plans without listing them.** Dynamic programming takes
  $`n \times B`$ steps: pseudo-polynomial, fast for small integer budgets and no escape from
  exponential growth.
- **Exponential growth outruns every polynomial.** LPs are solvable in polynomial time; MILPs are
  NP-hard, so no solver can promise to be fast on every model.
- **A search tree with a bound visits a sliver of the plans.** 5,862 nodes for 400 GridCap projects,
  against a tree of $`2^{401} - 1`$.
- **Size does not decide difficulty; the bound's strength does.** GridCap medium (400 binaries) is
  solved at the first node; a 30-binary puzzle with a weak relaxation is not solved in 100,000.

## Reference

| Term | Meaning |
| --- | --- |
| $`2^n`$ | the number of 0/1 plans of $`n`$ binaries |
| free project | one no rule but the budget touches; sets of them that fit give a lower bound on allowed plans |
| dynamic programming | build the answer for many sub-budgets from answers already computed |
| pseudo-polynomial | work grows with the size of the input's numbers, not their digits |
| polynomial / exponential | work grows like $`n^k`$ / like $`2^n`$ |
| NP-hard | no polynomial-time algorithm known, and one would solve a large family of hard problems |
| search tree | top node decides nothing; each level decides one variable; $`2^{n+1} - 1`$ nodes |
| branch-and-bound | a tree search that skips a node when a bound shows nothing below it can win |
| `result.solve_stats.node_count` | nodes a MathOpt solve explored |
| feasibility problem | a model with no objective: any plan that keeps the rows will do |

**Further reading:** [Mixed-Integer Programming (OR-Tools)](https://developers.google.com/optimization/mip) (OR-Tools' MIP solvers use branch-and-bound, and when to pick a MIP solver or CP-SAT); [MIP with arrays (OR-Tools)](https://developers.google.com/optimization/mip/mip_var_array) (the five-variable example and the node count its run reports); [The Knapsack Problem (OR-Tools)](https://developers.google.com/optimization/pack/knapsack) (the one-budget selection solved by a dedicated branch-and-bound knapsack solver); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.4: enumerating every integer point works only on tiny models; sections 9.5 and 9.7: branch-and-bound and implicit enumeration of 0-1 plans); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2.2: the strength of the LP relaxation, more than size, drives a branch-and-bound solver's work).

## Challenges

1. The tiny portfolio has 32 allowed plans of 256. Which rule removes the most? Count the plans that
   break each rule (lesson 3.1.1's `broken_rows` labels them).
2. The counting table has one entry per $10k of budget. How long would it be for GridCap medium with
   costs in dollars, and is that still practical?
3. In `tree_search.py`, change the order of the items from best ratio first to worst ratio first.
   Predict the node count at $`n = 20`$ before you run it.

## Design Note: Benchmark on Your Data, Not on Your Size

"How long will 400 projects take?" has no answer in general: GridCap medium needs one node and a
30-binary puzzle more than 100,000. The question that has an answer is "how long does *this model*
take on *these instances*", and the way to answer it is to run it on realistic data, several
seeds, and to keep the formulation's bound strong. Section 5's benchmarking lesson (5.4.2) and
section 11 make that a method.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**count_plans.py.** Traces the counting table on three projects, checks all 256 tiny plans, and
counts a lower bound on the allowed plans of small and medium (*Plans Double*, *A Table Over Budget
Amounts*). *Try:* Halve small's capital budget. Predict whether the count falls by about half or by
much more.

- Program: [count_plans.py](src/count_plans.py)

**growth_table.py.** Prints $`n^2`$, $`n^3`$ and $`2^n`$ side by side (*Exponential Growth*).
*Try:* Add a column for $`n^{10}`$. Predict the first $`n`$ in the table where $`2^n`$ passes it.

- Program: [growth_table.py](src/growth_table.py)

**tree_search.py.** Counts the nodes of a depth-first search over yes/no choices, with and without
the LP bound, on GridCap data and on equal-ratio data (*A Search Tree With a Bound*, *Size Does Not
Decide Difficulty*). *Try:* Use `p.value + 1` for the equal-ratio values. Predict whether the
search gets easier.

- Program: [tree_search.py](src/tree_search.py)

**split_hardness.py.** Solves GridCap's selection and the exact-split puzzle with HiGHS under a
node limit and prints each solve's node count (*Size Does Not Decide Difficulty*). *Try:* Give the
4-row puzzle an objective, `model.maximize(sum(x))`. Predict whether the node count changes.

- Program: [split_hardness.py](src/split_hardness.py)

**mip_arrays.py.** Adapted from the OR-Tools example `mip_var_array.py`; its last two lines are the
node counts of HiGHS and SCIP on that five-variable MIP (*Size Does Not Decide Difficulty*). *Try:*
Make every variable binary (`ub=1`). Predict whether HiGHS still needs more than one node.

- Program: [mip_arrays.py](src/mip_arrays.py)

**selection.py.** The selection model builder and `broken_rows`, shared with lessons 3.1.1 and
3.1.2.

- Library: [selection.py](src/selection.py)
