# 6.6.3 Incremental and Logarithmic Formulations

The lambda form of lesson 6.6.2 solved the falling-tier credit line exactly, with one binary per
segment. GridCap's planners now want volume-discount curves on the medium portfolio: each of the
three programs' contractors bills its total work on a curve with up to 16 tiers. That is 48 segment
binaries on top of 400 project binaries, and the planners ask whether there is a cheaper way to say
"the point lies on the curve". There are two, and each saves something different. This lesson
builds both, checks that they are exact, and measures what each costs and saves, in four rules.

GridCap is a fictional utility's portfolio, generated for this course; the credit line and the
volume discounts are invented.

## The Incremental Form Fills Segments in Order, With a Binary for Each Full One

Go back to lesson 6.6.1's segment variables and make them say what the credit line really does:
tier 2 is used only once tier 1 is full. Write each segment's use as a fraction
$`\phi_k \in [0, 1]`$ of its width, so

```math
b = X_0 + \sum_{k=1}^{K} (X_k - X_{k-1})\,\phi_k, \qquad y = F_0 + \sum_{k=1}^{K} (F_k - F_{k-1})\,\phi_k
```

and add a binary $`w_k`$ for each segment but the last, meaning "segment $`k`$ is full and segment
$`k+1`$ may start":

```math
\phi_{k+1} \le w_k \le \phi_k \qquad k = 1, \dots, K - 1, \qquad w_k \in \{0, 1\}
```

Read the two halves. $`w_k \le \phi_k`$: if $`w_k = 1`$, then $`\phi_k \ge 1`$, so segment $`k`$ is
full. $`\phi_{k+1} \le w_k`$: if $`w_k = 0`$, segment $`k+1`$ is empty. So the segments fill strictly
in order, each one full before the next starts, and every $`(b, y)`$ the rows allow is on the curve,
whatever its shape and whatever the push. This is the **incremental** (or **delta**) form. MIT's
*Applied Mathematical Programming* (section 9.2) writes the same rows with $`\delta_k`$ in units
instead of fractions, $`L_k w_k \le \delta_k \le L_k w_{k-1}`$ for a segment of length $`L_k`$.

```python
K = len(curve.xs) - 1
fill = [model.add_variable(lb=0, ub=1, name=f"{name}_fill{k}") for k in range(K)]
full = [model.add_binary_variable(name=f"{name}_full{k}") for k in range(K - 1)]
for k in range(K - 1):
    model.add_linear_constraint(fill[k + 1] <= full[k], name=f"{name}_next{k}")
    model.add_linear_constraint(full[k] <= fill[k], name=f"{name}_full{k}")
x = curve.xs[0] + sum((curve.xs[k + 1] - curve.xs[k]) * fill[k] for k in range(K))
y = curve.ys[0] + sum((curve.ys[k + 1] - curve.ys[k]) * fill[k] for k in range(K))
```

It needs $`K - 1`$ binaries, one fewer than the lambda form, and $`2(K-1)`$ rows. On the falling-tier
credit line of GridCap small it returns the same plan as the lambda form (next rule's table) and
fills the tiers in order:

```text
incremental fills [1.0, 1.0, 0.95] full [1, 1]
```

Tiers 1 and 2 full, 95% of tier 3: $`1{,}500 + 1{,}500 + 0.95 \times 2{,}000 = 4{,}900`$, the draw of
lesson 6.6.2.

The order rows are worth knowing apart from curves. Any rule of the form "stage $`k+1`$ may start
only when stage $`k`$ is complete" (capacity built in stages, a contract's volume bands, a crew's
qualification levels) is this pair of rows.

<!-- practice 1 -->

## A Gray Code Picks a Segment With About log2 K Binaries

The lambda form spends one binary per segment to say which segment is chosen, as a list of $`K`$
switches with one on. A list of $`m`$ binary digits can name $`2^m`$ different segments, so
$`m = \lceil \log_2 K \rceil`$ binaries are enough to name one of $`K`$ (2 for 4 segments, 4 for 16).
The **logarithmic** form keeps the lambda weights and replaces the $`K`$ segment binaries by $`m`$ bits.

The trick is which number each segment gets. Neighbouring segments share a breakpoint, and that
breakpoint must stay usable from both. That is the only reason for the ordering: it changes neither
the LP bound nor the order in which the solver branches on the bits. Number the segments with a **Gray code**, an ordering of the
$`m`$-bit numbers in which neighbours differ in exactly one bit (code $`s`$ is $`s \oplus \lfloor s/2
\rfloor`$, with $`\oplus`$ the bitwise exclusive or). Then, for each bit $`b`$:

- a breakpoint whose every segment has bit $`b = 1`$ may carry weight only if $`z_b = 1`$;
- a breakpoint whose every segment has bit $`b = 0`$ may carry weight only if $`z_b = 0`$;
- a breakpoint whose two segments differ in bit $`b`$ (there is exactly one such bit, by the Gray
  code) is not limited by bit $`b`$.

```math
\sum_{j \in L_b} \lambda_j \le z_b, \qquad \sum_{j \in R_b} \lambda_j \le 1 - z_b, \qquad z_b \in \{0, 1\}, \qquad b = 0, \dots, m-1
```

with $`L_b`$ the breakpoints of the first kind and $`R_b`$ of the second, plus the weights' own rows
from lesson 6.6.2. The program prints the codes and sets for 4 segments, then fixes each code and
asks HiGHS which breakpoints may carry weight:

```text
4 segments: segment s runs from breakpoint s to s+1
segment codes (bit1 bit0): {0: '00', 1: '01', 2: '11', 3: '10'}
bit 0: breakpoints [2] need z_0 = 1, breakpoints [0, 4] need z_0 = 0
bit 1: breakpoints [3, 4] need z_1 = 1, breakpoints [0, 1] need z_1 = 0
z_1 z_0 = 00: weight allowed on breakpoints [0, 1]
z_1 z_0 = 01: weight allowed on breakpoints [1, 2]
z_1 z_0 = 10: weight allowed on breakpoints [3, 4]
z_1 z_0 = 11: weight allowed on breakpoints [2, 3]
```

Take breakpoint 1: it ends segment 0 (code 00) and starts segment 1 (code 01). Both have bit 1 = 0,
so breakpoint 1 is in $`R_1`$ and needs $`z_1 = 0`$; they differ in bit 0, so bit 0 leaves it free.
Each of the four codes opens exactly one segment's two ends, which is the neighbour rule. With a
plain binary count (00, 01, 10, 11) instead, segments 1 and 2 would differ in two bits, and their
shared breakpoint would be limited by neither, so it could carry weight next to any segment.

When $`K`$ is not a power of 2, some codes name no segment; the rows then allow weight on no
breakpoint, and since the weights must add up to 1, those codes are infeasible. The program checks
every code for 2 to 9 segments:

```text
segments | binaries | every code allows one segment's two ends, unused codes none
       2 |        1 | True
       3 |        2 | True
       4 |        2 | True
       5 |        3 | True
       6 |        3 | True
       7 |        3 | True
       8 |        3 | True
       9 |        4 | True
```

The library's version:

```python
def gray(s: int) -> int:
    """The s-th Gray code: neighbours differ in exactly one bit."""
    return s ^ (s >> 1)
```

```python
for b, (ones, zeros) in enumerate(log_sets(n - 1)):
    z.append(model.add_binary_variable(name=f"{name}_bit{b}"))
    model.add_linear_constraint(sum(lam[j] for j in ones) <= z[b], name=f"{name}_one{b}")
    model.add_linear_constraint(sum(lam[j] for j in zeros) <= 1 - z[b], name=f"{name}_zero{b}")
```

Vielma's survey (section 9) covers formulations with a logarithmic number of binaries, and Pyomo's
`Piecewise` offers this one as `pw_repn="LOG"` (lesson 6.6.4 runs it); Pyomo's documentation credits
it to Vielma and Nemhauser.

<!-- practice 2 -->

## All Three Forms Give the Same LP Bound Here

The **LP bound** of a MILP is the optimum of its LP relaxation, the same model with every integer
variable relaxed to an interval (lesson 3.3.1); for a maximization it is an upper bound on the MILP,
and the closer it is, the less the search has to do (lesson 6.4.3 compared two forms by it). The
program writes the falling-tier credit line three ways, and also solves the relaxation of the
weights-only rows of lesson 6.6.2, which is the loosest a curve can be while still passing through
its breakpoints:

```text
form        | curve binaries | rows | MILP      | LP bound   | drawn
lambda      |              3 |   15 | $26,753k | $26,959.1k | $4,900k
incremental |              2 |   13 | $26,753k | $26,959.1k | $4,900k
log         |              2 |   14 | $26,753k | $26,959.1k | $4,900k
LP bound with weights only, no curve binaries at all: $26,959.1k
```

Same plan, same MILP optimum, and the same LP bound for all three, equal to the bound of the
weights-only rows. Relaxed, the weights-only rows allow every convex combination of the
breakpoints: the smallest convex region that contains the curve, its **convex hull**. No
formulation that contains the curve can relax to anything smaller, so that bound is the best a
formulation of the curve can give. Vielma calls a formulation whose LP relaxation reaches this best
bound **sharp** (his Definition 2.2). He shows that the incremental form is locally ideal, a
stronger property that implies sharpness (section 8, and Proposition 2.4); the table shows the
lambda and log forms reaching the same bound on this curve. The project binaries still leave a gap, $26,959.1k against $26,753k, and no
way of writing the curve can close it.

So on the LP bound, the formulations tie. What differs is their size, and how the search behaves.

## Fewer Binaries Is Not Fewer Nodes

The medium portfolio, with each program's contractor billing its total list-price work on a curve
whose rate falls evenly from 1.00 to 0.60 per $k across $`K`$ equal tiers. The three invoices must fit
80% of the capital budget. HiGHS solves each form to a zero gap and reports its branch-and-bound
node count, the number of subproblems its search tree held (a node is one LP of branch and bound,
lesson 3.2.1):

```text
GridCap medium, 400 projects, invoices within $296,696k
 K | form        | curve binaries | rows | MILP       | LP bound     | nodes
 4 | lambda      |             12 |  100 | $203,664k | $229,757.7k | 4,385
 4 | incremental |              9 |   97 | $203,664k | $229,757.7k |     1
 4 | log         |              6 |   94 | $203,664k | $229,757.7k | 2,140
 8 | lambda      |             24 |  112 | $207,006k | $229,757.7k | 4,005
 8 | incremental |             21 |  121 | $207,006k | $229,757.7k |     7
 8 | log         |              9 |  100 | $207,006k | $229,757.7k |   312
16 | lambda      |             48 |  136 | $208,484k | $229,757.7k | 6,432
16 | incremental |             45 |  169 | $208,484k | $229,757.7k |     0
16 | log         |             12 |  106 | $208,484k | $229,757.7k |   742
```

Every form reaches the same optimum, and all share one LP bound. The log form has by far the fewest
binaries (12 against 48 at $`K = 16`$) and the fewest rows. But the search tells another story: the
incremental form needed at most 7 nodes (0 means HiGHS closed the gap at the root, before
branching), the log form hundreds to thousands, the lambda form thousands.

Why can the form with the most binaries be the quickest? Look at what one branch does. In the
incremental form, $`w_{k+1} \le \phi_{k+1} \le w_k`$, so the binaries are ordered: branching on
$`w_k = 0`$ forces every later $`w`$ to 0, and $`w_k = 1`$ forces every earlier one to 1. Either side
of the branch settles a whole run of binaries. In the lambda form, $`z_k = 1`$ fixes all the others,
but $`z_k = 0`$ removes only one segment of $`K`$. Vielma (section 8) explains the incremental form's
fewer nodes in the same terms, citing computational studies.

Do not read the table as a law. Node counts depend on the instance, the solver and its version, even
on the order the rows are written in, and these are three curves in one model on one portfolio. What
the table does show is that the number of binaries does not predict the search: measure the
formulations on your own instances before choosing, as lesson 6.4.3 did for precedence rows.

## The Model

The selection model of lesson 1.1.1 on GridCap small with the falling-tier credit line in
incremental form, marked. `forms_compared.py` also solves it with the lambda and log forms, which
change only the marked lines (lesson 6.6.2 and the Gray-code rule above).

**Sets.** $`P`$ the candidate projects; $`M`$, $`C`$ and $`\mathcal{G}`$ the must-do projects, the
child projects (parent $`p(c)`$) and the alternative groups; $`k = 1, \dots, K`$ the credit line's
segments ($`K = 3`$). ← this lesson

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ ($k); $`B = 38{,}390`$ ($k); $`(X_k, F_k)`$,
$`k = 0, \dots, K`$, the breakpoints: (0, 0), (1,500, 675), (3,000, 1,050), (5,000, 1,250).
← this lesson

**Variables.**

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(1 if project } i \text{ is funded)} \\
& 0 \le \phi_k \le 1 && k = 1, \dots, K && \text{(share of tier } k \text{ drawn)} \quad \leftarrow \text{this lesson} \\
& w_k \in \{0, 1\} && k = 1, \dots, K - 1 && \text{(1 if tier } k \text{ is full)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i - \Big(F_0 + \sum_{k=1}^{K} (F_k - F_{k-1})\,\phi_k\Big)
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B + X_0 + \sum_{k=1}^{K} (X_k - X_{k-1})\,\phi_k && && \text{(budget)} \quad \leftarrow \text{this lesson} \\
\phi_{k+1} &\le w_k && k = 1, \dots, K - 1 && \text{(loan\_next}_k) \quad \leftarrow \text{this lesson} \\
w_k &\le \phi_k && k = 1, \dots, K - 1 && \text{(loan\_full}_k) \quad \leftarrow \text{this lesson} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

In the code, $`\phi_k`$ is `loan_fill{k-1}` and $`w_k`$ is `loan_full{k-1}`.

## Summary

- **The incremental form fills segments in order, with a binary for each full one.**
  $`\phi_{k+1} \le w_k \le \phi_k`$; $`K - 1`$ binaries; the same rows state any "next stage only
  after this one is complete" rule.
- **A Gray code picks a segment with about $`\log_2 K`$ binaries.** Each bit limits the breakpoints
  whose segments agree on it; neighbours differ in one bit, so their shared breakpoint stays usable.
- **All three forms give the same LP bound here.** Each reached the bound of the curve's convex
  hull, the best any formulation can give (sharp), so the choice between them is not about the bound.
- **Fewer binaries is not fewer nodes.** On GridCap medium the incremental form needed at most 7
  nodes, the log form up to 2,140 and the lambda form up to 6,432; measure on your own instances.

## Reference

| Form | Continuous | Binaries | Rows (besides the curve's own) | Exact for |
| --- | --- | --- | --- | --- |
| segments (6.6.1) | $`K`$ | 0 | 0 | convex pushed down, concave pushed up |
| lambda (6.6.2) | $`K + 1`$ | $`K`$ | $`K + 3`$ | any curve, any push |
| incremental | $`K`$ | $`K - 1`$ | $`2(K - 1)`$ | any curve, any push |
| logarithmic | $`K + 1`$ | $`\lceil \log_2 K \rceil`$ | $`1 + 2\lceil \log_2 K \rceil`$ | any curve, any push |

| Term | Meaning |
| --- | --- |
| incremental (delta) form | segments as fractions $`\phi_k`$, filled in order through $`\phi_{k+1} \le w_k \le \phi_k`$ |
| Gray code | an ordering of $`m`$-bit numbers in which neighbours differ in one bit |
| sharp | a formulation whose LP relaxation gives the best bound any formulation of the set can |
| node | one LP subproblem of branch and bound (lesson 3.2.1) |

**Further reading:** [MathOpt `Model` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_binary_variable` and `add_linear_constraint`); [MathOpt sample integer_programming.py (OR-Tools)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py) (solving a MIP and checking its termination before reading values); [Vielma, Mixed Integer Linear Programming Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) (section 2: sharp and locally ideal formulations; section 8: incremental formulations; section 9: logarithmic formulations); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (section 9.2: the incremental rows, with a binary per segment that is 1 when the segment before it is full); [Pyomo `Piecewise`](https://pyomo.readthedocs.io/en/stable/api/pyomo.core.base.piecewise.Piecewise.html) (its `pw_repn` options, CC, INC, LOG and others, and the default SOS2).

## Challenges

1. Write the incremental rows for a curve with $`K = 1`$. How many binaries, and why?
2. Number 8 segments with a plain binary count instead of the Gray code, and use `log_codes.py`'s
   check to find a code that allows weight on three breakpoints.
3. In `medium_discounts.py`, change the falling rates to rising ones (0.60 up to 1.00). Predict the
   node counts of each form, then measure.

## Design Note: Keep Every Formulation Behind One Signature

`add_lambda`, `add_incremental` and `add_log` take the same arguments and return the same `Piece`:
the expressions for $`x`$ and $`y`$ and the binaries used. The model never knows which one built its
curve, so `forms_compared.py` and `medium_discounts.py` switch formulations by passing a different
function, and the tests check every form against the same points. When a new instance solves
slowly, trying another formulation is then a one-word change, and the measurement is cheap enough to
make before arguing about which form "should" be faster.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**forms_compared.py.** Solves the falling-tier credit line on GridCap small with the lambda,
incremental and log forms, and their LP relaxations (*The Incremental Form*, *All Three Forms Give
the Same LP Bound Here*). *Try:* Relax only the curve's binaries and keep the projects integer.
Predict whether the three bounds still agree.

- Program: [forms_compared.py](src/forms_compared.py)

**log_codes.py.** Prints the Gray codes and the bit sets for 4 segments, then checks every code for
2 to 9 segments (*A Gray Code Picks a Segment*). *Try:* Replace `gray(s)` by `s` in `log_sets`.
Predict the first number of segments where the check fails.

- Program: [log_codes.py](src/log_codes.py)

**medium_discounts.py.** Three discount curves on GridCap medium, each form at 4, 8 and 16 tiers,
with node counts (*Fewer Binaries Is Not Fewer Nodes*). *Try:* Set `SHARE` to 0.9. Predict whether
the incremental form still needs the fewest nodes.

- Program: [medium_discounts.py](src/medium_discounts.py)

**piecewise.py.** The curve and the formulations; `add_incremental`, `gray`, `log_sets` and `add_log`
are this lesson's.

- Library: [piecewise.py](src/piecewise.py)
