# 3.2.3 Node and Variable Selection

GridCap's planners move from one capital budget to a budget for each of the five years 2027 to
2031, on the small portfolio. The model gets four more rows, and the branch-and-bound of lessons
3.2.1 and 3.2.2 still finds the best plan. But the same search can take 147 nodes or 10,425,
depending on two choices the earlier lessons made without comment: which waiting node to solve
next, and which fractional variable to split. Neither choice changes the answer; both change the
work, sometimes by a factor of 70. This lesson names the classic rules for each choice, runs every
combination on the same model, and reads what the numbers say.

## The Model

The selection model of lesson 3.2.1, with the one capital budget row replaced by one row per year.
Every project starts in its earliest year, as in the one-period model, and spends its cost profile
from there.

**Sets.** $`P`$, the projects (40 on small); $`Y`$, the plan's years (2027 to 2031);
$`M \subseteq P`$, the must-do projects; $`C \subseteq P`$, the projects with a parent $`p(c)`$;
$`\mathcal{G}`$, the alternative groups.

**Parameters.** $`v_i`$, the value of project $`i`$ ($k); $`s_{i,y}`$, what project $`i`$ spends in
year $`y`$ if it starts in its earliest year $`e_i`$, that is its cost profile's entry for year
$`y - e_i`$, or 0 when the project is not being worked on in $`y`$ ($k); $`B_y`$, the budget of
year $`y`$ ($k).

A project's **cost profile** is its spend in each year of work, in order: entry 0 for its first year,
entry 1 for its second, and so on. GridCap stores it with each project, and `p.spend(start)` turns it
into a year-by-year dict. One project of GridCap small (`cost_profile.py`):

```text
P013: earliest start e = 2028, cost profile [440, 330, 240] ($k by year of work)
  s[P013,2027] =     0   not worked
  s[P013,2028] =   440   profile[0]
  s[P013,2029] =   330   profile[1]
  s[P013,2030] =   240   profile[2]
  s[P013,2031] =     0   not worked
```

So $`x_{P013}`$ appears in `budget_2028`, `budget_2029` and `budget_2030`, with coefficients 440,
330 and 240.

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

**Objective and constraints.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, x_i \\
\text{s.t. }& \sum_{i \in P} s_{i,y}\, x_i \le B_y \quad \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{this lesson} \\
& x_i = 1 \quad \forall i \in M && \text{(must}_i) \\
& x_c \le x_{p(c)} \quad \forall c \in C && \text{(parent}_c) \\
& \textstyle\sum_{i \in g} x_i \le 1 \quad \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The rows are named `budget_2027` to `budget_2031`; `build(small, yearly=True)` in `selection.py`
(shown in lesson 3.2.1) makes them. HiGHS's optimum for this model is 22,532.

## The Node Rule Decides Which Waiting Node Comes Next

Every time a node is branched, its two children join the list of **waiting** nodes: made, but not
yet solved. The **node rule** (also called node selection) picks which waiting node to solve next.
The three classic rules:

| Rule | Takes next | Kept in |
| --- | --- | --- |
| depth-first | the deepest waiting node, the newest among equals | a stack (last in, first out) |
| best-first (best bound) | the node with the highest bound, the oldest among equals | a heap ordered by bound |
| breadth-first | the oldest waiting node | a queue (first in, first out) |

A waiting node's bound is its parent's LP value, since its own LP is not solved yet (lesson 3.2.2).
In `bnb.py` the rule is a small class:

```python
class Open:
    """The nodes waiting to be solved, handed out in the order the node rule asks for."""

    def __init__(self, rule: str) -> None:
        self.rule, self.items, self.heap = rule, [], []

    def push(self, node: Node) -> None:
        if self.rule == "best":
            heapq.heappush(self.heap, (-node.bound, node.id, node))
        else:
            self.items.append(node)

    def pop(self) -> Node:
        if self.rule == "best":
            return heapq.heappop(self.heap)[2]
        return self.items.pop() if self.rule == "depth" else self.items.pop(0)
```

A list used as a stack (`pop()`) is depth-first: the node just pushed is the deepest one waiting,
because it is a child of the node just solved. `pop(0)` turns the list into a queue, which is
breadth-first. Python's `heapq` always hands out the smallest entry, so best-first stores
`-node.bound` to get the largest bound first, and `node.id` breaks ties in favour of the older
node. Every search in lessons 3.2.1 and 3.2.2 was depth-first.

On tiny, best-first goes like this:

```text
  0 root                        LP 3,770.1  branch on x_P003 = 0.099
  1   x_P003 = 0                LP 3,695.5  branch on x_P008 = 0.500
  2   x_P003 = 1                LP 3,054.7  branch on x_P004 = 0.633
  3     x_P008 = 0              LP 3,627.0  integral: new incumbent 3,627
  4     x_P008 = 1              LP 3,617.6  pruned: bound 3,617.6 cannot beat 3,627
  5     x_P004 = 0              not solved  pruned before its LP: parent bound cannot beat the incumbent
  6     x_P004 = 1              not solved  pruned before its LP: parent bound cannot beat the incumbent
best-first :  7 nodes,  5 LPs, at most 4 waiting, best 3,627
depth-first: 21 nodes, 21 LPs, at most 4 waiting, best 3,627
```

Nodes 1 and 2 both wait with the root's bound 3,770.1, so the older, node 1, goes first. After it,
node 2 (bound 3,770.1) beats nodes 3 and 4 (bound 3,695.5) and is solved, at 3,054.7. Then node 3
holds the best bound and turns out to be the optimal plan. From there every waiting bound is below
3,627: node 4 is solved and pruned, and nodes 5 and 6, whose parent bound was 3,054.7, are pruned
without solving their LPs at all. Five LPs instead of 21.

On the small portfolio with yearly budgets, branching on the first fractional variable each time:

```text
small: 40 projects, budgets 2027 $8,890k, 2028 $8,120k, 2029 $8,760k, 2030 $8,610k, 2031 $7,850k
node rule  nodes    LPs most waiting first plan at node    best
depth      1,705  1,705           14                 47  22,532
best       1,065    587          504                554  22,532
breadth   10,425  6,963        3,366              5,196  22,532
```

`nodes` counts every node taken from the waiting list, `LPs` the ones whose LP was solved (the rest
were pruned on their parent's bound), `most waiting` the largest size the waiting list reached, and
`first plan at node` how many nodes were taken before the first incumbent. All three find 22,532,
HiGHS's optimum. The next three rules read the table.

## Depth-First Keeps Few Nodes Waiting and Reaches a Plan Quickly

Depth-first never had more than 14 nodes waiting. Each step down the tree leaves one sibling
waiting, so the list holds at most about one node per level of the current path, and a 0-1 tree
on 40 variables has at most 40 levels. Memory stays small no matter how big the tree grows.

It also found its first plan at node 47, against 554 for best-first. Diving fixes one more variable
at every step, and with enough variables fixed the LP has no room left to be fractional, so plans
appear at the bottom of the first dive. An early plan matters for two reasons: it lets the bound
test start pruning (lesson 3.2.2), and if the search is stopped early, there is a plan to hand
the planners.

The cost is the number of nodes: 1,705, and every one needed its LP solved. Depth-first finishes one
subtree before looking at any other, so if it dives into a poor region it searches that region to
the bottom, with a weak incumbent that prunes little. The tiny run in lesson 3.2.2 did exactly that:
13 nodes under $`x_{P003} = 1`$ before reaching the side of the tree where the optimum was.

## Best-First Solves the Fewest Nodes Because It Never Opens a Node Below the Optimum

Best-first took 1,065 nodes and solved only 587 LPs: 478 nodes were pruned on their parent's bound
without an LP. There is a short argument for why best-first is economical.

Take any node whose bound is above the optimum $`z^*`$. No search with these branching decisions
can prune it: the bound test needs an incumbent of at least its bound, and no plan is worth more
than $`z^*`$. So every search must solve such nodes. Best-first solves almost nothing else. It
always takes the highest bound, so while any waiting bound is above $`z^*`$ it takes one of those;
once the optimum is the incumbent, every remaining bound at or below it is pruned without its LP.
Apart from ties at $`z^*`$ itself, the nodes best-first solves are exactly the ones every search
must solve.

The cost is memory and late plans. The highest bounds sit near the top of the tree, so best-first
keeps going back to shallow nodes and leaves their deep children waiting: 504 waiting at once,
36 times depth-first's 14. On large models that list can outgrow the machine's memory. And plans
live at the bottom of the tree, so the first one came only at node 554. Stop the search at node
500 and best-first has nothing to show.

## Breadth-First Is the Rule to Avoid

Breadth-first solves every node of one depth before any node of the next. It took 10,425 nodes and
held 3,366 waiting. It shares best-first's flaw (plans come only from the bottom, so it found the
first one at node 5,196 and pruned little before then) without its reason (the order ignores the
bounds). It appears here as a baseline.

A common design mixes the first two rules: dive depth-first from a node for a while to find plans,
then jump back to a node with a high bound. Lesson 3.3.3
looks at diving as a way of finding plans.

<!-- practice 1 -->

## The Variable Rule Decides Which Fractional Variable to Split

When a node's LP has several fractional variables, the **variable rule** (also called branching
variable selection) picks the one to branch on. Every choice is correct, since every split keeps
all plans (lesson 3.2.1); the choice changes how fast the bounds fall. `bnb.py` has three rules:

```python
def choose_variable(sel: Selection, node: Node, lp: LP, rule: str, search: Search) -> str:
    """The fractional variable to branch on."""
    candidates = fractional(lp.x)
    if rule == "first":
        return candidates[0]
    if rule == "most":
        return max(candidates, key=lambda name: min(lp.x[name], 1 - lp.x[name]))
    if rule == "strong":
        def drop(name: str, value: int) -> float:
            search.lps += 1
            child = solve_lp(sel, {**node.fixed, name: value})
            return math.inf if child.value is None else lp.value - child.value
        return max(candidates, key=lambda name: max(drop(name, 0), EPS) * max(drop(name, 1), EPS))
    raise ValueError(f"unknown variable rule {rule!r}")
```

- **First** takes the first fractional variable in the model's order. It is cheap and blind.
- **Most fractional** takes the variable whose value is closest to 0.5: `min(v, 1 - v)` is its
  distance to the nearer of 0 and 1, and the rule takes the largest. The idea is that the LP is
  least sure about it. `max` keeps the first variable among ties.
- **Strong branching** tries each candidate: it solves both children's LPs and measures how far
  each child's value **drops** below the node's. It takes the candidate with the largest product of
  its two drops. The next rule explains why the product.

A variable rule only matters when there is a choice. On the one-row model of lesson 3.2.2 the LP
rarely has more than one or two fractional variables, because the budget row can hold only one
project at a fraction (plus any project tied to it by a parent or alternative row). Each yearly
row can hold one of its own:

```text
one capital budget row  : at most 2 fractional variables at a node
one budget row per year : at most 5 fractional variables at a node
```

That is why this lesson uses the yearly model: with 5 rows there are real choices to make.

<!-- practice 2 -->

## Strong Branching Buys a Smaller Tree With Extra LPs

Every combination of the three node rules and three variable rules, on small with yearly budgets:

```text
node rule variable rule  nodes    LPs most waiting first plan at node
depth     first          1,705  1,705           14                 47
depth     most           1,991  1,991           15                 50
depth     strong         1,291  3,667           13                 53
best      first          1,065    587          504                554
best      most             693    453          251                232
best      strong           147    375           72                 72
breadth   first         10,425  6,963        3,366              5,196
breadth   most           6,993  4,229        2,839              3,960
breadth   strong         2,961  7,169        1,259              1,630
best plan of each run: 22,532
```

Memory follows the node rule, not the variable rule. Whatever the variable rule, depth-first kept
at most 15 nodes waiting, best-first between 72 and 504, and breadth-first between 1,259 and 3,366.
A better variable rule shrinks best-first's list, but it stays far above depth-first's.

The `LPs` column counts strong branching's trial LPs too. Strong branching made the smallest tree
under every node rule. Under best-first it cut the tree from 1,065 nodes to 147, and even with its
trial LPs counted it solved fewer LPs (375) than the other rules. Under depth-first it saved
nodes (1,291 against 1,705) but more than doubled the LPs (3,667). This program also wastes some
of that work: the trial LPs of the chosen variable are the children's LPs, and it solves them again
when the children are taken. A solver keeps them.

Why the product of the drops? A split is useful when it lowers the bound on *both* sides: then
both children are more likely to be pruned. Take two candidates. Splitting $`x_a`$ drops the bound
by 30 in one child and 0.1 in the other; splitting $`x_b`$ drops it by 6 and 5. The sum prefers
$`x_a`$ (30.1 against 11), but $`x_a`$'s second child is almost the parent again, so nearly nothing
was gained on that side. The product prefers $`x_b`$ (30 against 3). Lifting each drop to at least
$`\varepsilon`$ keeps one zero drop from making every candidate score 0. A child that is infeasible
counts as an infinite drop: that side of the tree is gone, the best outcome there is.

Strong branching on every candidate at every node is expensive, so a search can estimate the drops
instead. A common estimate is the **pseudo-cost**: the average drop per unit of change seen each
time a variable was branched on before. Pseudo-costs cost nothing to apply but know nothing at the
start, so a typical design uses strong branching on a variable until it has been branched on a few
times, then trusts its pseudo-cost. That idea is usually called **reliability branching**. HiGHS
documents its threshold as the option `mip_pscost_minreliable`, "minimal number of observations
before MIP solver pseudo costs are considered reliable", 8 by default; lesson 3.3.4's HiGHS log
counts the LP iterations its strong branching spent.

<!-- practice 3 -->

## No Rule Wins Everywhere, So Measure on Your Own Model

The table has surprises. Most-fractional made the tree larger than first-fractional under
depth-first (1,991 against 1,705) and smaller under best-first (693 against 1,065). Strong branching
saved LPs under best-first and cost LPs under depth-first. None of these results is a law: they are
measurements on one model, and a different portfolio or one more row could reorder them. What holds
generally is the shape of the trade-offs:

| Rule | Gains | Pays |
| --- | --- | --- |
| depth-first | little memory, plans early | more nodes when the first dives are poor |
| best-first | fewest nodes that must be solved | memory, and no plan until late |
| breadth-first | nothing | memory, late plans, many nodes |
| first or most fractional | free | blind to how much a split helps |
| strong branching | the largest bound drops, so small trees | two trial LPs per candidate |
| pseudo-costs | strong branching's aim at no cost | poor guesses until history builds up |

When a model is slow in a real solver, these are among the settings worth trying, and the way to
choose is the way this lesson chose: run each option on the same instances and count. MathOpt has
one solver-independent handle on them, `ModelSolveParameters(branching_priorities=...)`: variables
given higher values are branched on first, and the rest keep the solver's default priority. Any
other control over these rules, where a solver offers one, is in that solver's own parameters. Section 5's
lesson on honest benchmarking (5.4.2) shows how to do that fairly over several instances and seeds.

## Summary

- **The node rule decides which waiting node comes next.** Depth-first uses a stack, best-first a
  heap ordered by bound, breadth-first a queue.
- **Depth-first keeps few nodes waiting and reaches a plan quickly**, but can spend many nodes in a
  poor part of the tree.
- **Best-first solves the fewest nodes because it never opens a node below the optimum**, but holds
  many nodes waiting and finds its first plan late.
- **Breadth-first is the rule to avoid.**
- **The variable rule decides which fractional variable to split.** It matters only when the LP has
  several fractional variables, which needs several rows.
- **Strong branching buys a smaller tree with extra LPs.** It scores each candidate by the product
  of its two children's bound drops; pseudo-costs estimate those drops from history.
- **No rule wins everywhere, so measure on your own model.**

## Reference

| Rule | Picks |
| --- | --- |
| depth-first | deepest waiting node; newest among equals |
| best-first | highest bound (parent's LP value); oldest among equals |
| breadth-first | oldest waiting node |
| first fractional | the first fractional variable in model order |
| most fractional | $`\arg\max_j \min(x_j - \lfloor x_j \rfloor,\ \lceil x_j \rceil - x_j)`$ |
| strong branching | $`\arg\max_j \max(\Delta_j^-, \varepsilon) \cdot \max(\Delta_j^+, \varepsilon)`$, with $`\Delta`$ the drop of each child's LP value |
| pseudo-cost | strong branching's score with each drop estimated from past branchings |

| Small, yearly budgets | Nodes | LPs |
| --- | --- | --- |
| depth-first, first fractional | 1,705 | 1,705 |
| best-first, strong branching | 147 | 375 |
| breadth-first, first fractional | 10,425 | 6,963 |

**Further reading:** [MathOpt `ModelSolveParameters` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model_parameters.py) (branching priorities and solution hints, the two per-model search settings MathOpt passes to a solver); [HiGHS option definitions](https://ergo-code.github.io/HiGHS/dev/options/definitions/) (`mip_pscost_minreliable` and the other MIP search options HiGHS exposes); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.5: taking the subdivision with the largest LP value, the last-generated-first-analyzed rule, and looking one dual-simplex step ahead to choose the branching variable); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2.2: how the effect of branching on a formulation shapes a solver's work).

## Challenges

1. On tiny, best-first solved 5 LPs. Which nodes of lesson 3.2.2's depth-first tree have a parent
   bound above 3,627, and how many are there? Compare with the argument in the best-first section.
2. Add a node rule "best-first, but dive": take the best node, then keep taking its up child until
   the dive ends. Predict where it lands in the table, then add it to `Open` and run it.
3. Strong branching here tries every fractional variable. Change it to try at most the 2 most
   fractional ones. Predict nodes and LPs under best-first.

## Design Note: Why a Waiting Node Carries Its Parent's Bound

A waiting node's own LP would give a tighter bound, and best-first would order nodes better with it.
But solving a node's LP when it is made, rather than when it is taken, solves the LP of every node
that is later pruned on its parent's bound: 478 of them in the best-first run above. Storing the
parent's value is free, which is why this module's search keeps it. A refinement is to store an
estimate as well (the parent's bound minus the pseudo-cost of the branching), which ranks waiting
nodes better at no LP cost.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**cost_profile.py.** One project's cost profile and the $`s_{i,y}`$ entries the yearly budget rows
take from it (*The Model*). *Try:* Pick a project whose earliest start is 2030 and whose profile has
three entries. Predict which of its entries no budget row of 2027 to 2031 uses.

- Program: [cost_profile.py](src/cost_profile.py)

**best_first.py.** The tiny tree taken best-first, with the depth-first count beside it (*The Node
Rule Decides Which Waiting Node Comes Next*). *Try:* Break best-first's ties toward the newer node
(use `-node.id`). Predict whether the node count changes.

- Program: [best_first.py](src/best_first.py)

**node_rules.py.** The three node rules on small with yearly budgets (*The Node Rule Decides Which
Waiting Node Comes Next* and the three sections after it). *Try:* Start every run from the rounded
root plan of lesson 3.2.2. Predict which rule gains the most.

- Program: [node_rules.py](src/node_rules.py)

**variable_rules.py.** Counts the fractional variables per node in both models, then runs all nine
combinations of rules (*The Variable Rule Decides Which Fractional Variable to Split* and *Strong
Branching Buys a Smaller Tree With Extra LPs*). *Try:* Run the nine combinations on the one-row
model instead. Predict how much the variable rule matters there.

- Program: [variable_rules.py](src/variable_rules.py)

**bnb.py.** The branch-and-bound library: `Open` holds the node rules, `choose_variable` the
variable rules.

- Library: [bnb.py](src/bnb.py)
