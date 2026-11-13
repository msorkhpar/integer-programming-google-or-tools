# 9.1.3 IIS With MathOpt, gurobipy and Pyomo

The pre-solve checks of lesson 9.1.2 found one cause in GridCap's Budget Lock scenario, P017's
crews. With those crews restored the model was still infeasible, and no check could say why. The
planners now need the rules that clash, by name, and they want to know that the answer does not
depend on which tool produced it. This lesson asks three tools for an **irreducible infeasible
subsystem** (IIS) of the same model: MathOpt with a hand-written filter, gurobipy's `computeIIS`,
and Pyomo's two tools. It compares their answers. They do not agree, and each disagreement has a
reason worth knowing. GridCap is a fictional utility; none of its numbers are real.

Lesson 4.3.5 already showed two things this lesson builds on. MathOpt's
`compute_infeasible_subsystem` is refused by every solver that loads in the runner, and Gurobi
cannot be loaded through MathOpt in OR-Tools 9.15: `SolverType.GUROBI` raises
`RuntimeError: bad_function_call`, because this MathOpt cannot load the Gurobi 13 library in the
runner. It also found an IIS by hand with a deletion filter on another scenario. gurobipy's
`computeIIS` was introduced in lesson 5.3.3, and Pyomo's IIS tools in lesson 5.1.4. Here the same
ideas are compared head to head on one scenario that has more than one conflict.

## The Model

The model is lesson 9.1.1's, unchanged: its full formulation is there, with every row's label.
The IIS works on its 70 named rows, and on the bounds and integrality of its 80 variables
$`x_{i,t} \in \{0, 1\}`$. The rows the answers below name:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &= 1 && i \in \{\text{P017}, \text{P039}\} && \text{(must}_i) \\
x_{\text{P023},2029} &\le \sum_{s \in T_{\text{P022}},\, s \le 2028} x_{\text{P022},s} && && \text{(after}_{\text{P023},2029}) \\
\sum_{i \in P} \sum_{t \in T_i} c_{i,\,2028-t}\, x_{i,t} &\le 6{,}000 && && \text{(budget}_{2028}) \\
\sum_{i:\, q(i) = q} \ \sum_{t \in T_i,\ t \le y < t + d_i} m_i\, x_{i,t} &\le K_{q,y} && (q, y) \text{ as named} && \text{(crews}_{q,y}) \\
\sum_{t \in T_{\text{P023}}} x_{\text{P023},t} &\ge 1 && && \text{(force}_{\text{P023}}) \\
x_{\text{P032},2028} &\ge 1 && && \text{(force}_{\text{P032},2028})
\end{aligned}
```

P023's window is the single year 2029 and its lag behind P022 is one year, so its precedence row
for 2029 says "P023 in 2029 needs P022 started by 2028". The Budget Lock scenario sets
$`K_{\text{transmission},2030} = K_{\text{transmission},2031} = 12`$. The other crew rows keep
GridCap's figures: $`K_{\text{transmission},2028} = 19`$ and $`K_{\text{distribution},2030} = 8`$.

## An IIS Is One Conflict: Irreducible, but Neither Unique nor the Smallest

An IIS is a set of the model's constraints (rows, variable bounds, and for a MIP the integrality of
variables) with two properties:

1. **infeasible**: no point meets all of them;
2. **irreducible**: drop any one member and the rest can all be met.

Irreducible does not mean smallest. A model can have many IISs of different sizes, and a tool
returns one of them. Gurobi's reference for `computeIIS` says so: the result is not necessarily
the smallest IIS. Nor is an IIS the whole story. It explains one reason the model is infeasible,
and other reasons can remain after it is fixed. Both facts show up on the Budget Lock scenario.

## The Deletion Filter Keeps the Conflict It Tests Last

The **deletion filter** (John Chinneck's method, which Pyomo's documentation names as the source
of its own tool) starts from all the rows and drops them one at a time. If the rest is still
infeasible, the row was not needed and stays out. If the rest becomes feasible, the row goes back.
`filters.Oracle` answers each "is this set of rows infeasible?" question. It works on a
zero-objective copy (lesson 9.1.1) and switches a row off by removing both of its bounds:

```python
    def infeasible(self, active) -> bool:
        active = set(active)
        for name, row in self.rows.items():
            lower, upper = self.bounds[name] if name in active else (-math.inf, math.inf)
            row.lower_bound, row.upper_bound = lower, upper
        self.solves += 1
        return solve(self.work, self.solver).termination.reason in (R.INFEASIBLE, R.INFEASIBLE_OR_UNBOUNDED)
```

The variables keep their bounds and integrality throughout. They are what makes $`x_{i,t}`$ a
yes-or-no decision, not rules a planner wrote. So the IIS this filter finds is a set of rows, read
together with every bound. The filter itself:

```python
def deletion_filter(oracle: Oracle, rules: list[str]) -> list[str]:
    """Drop each rule in turn; keep it out if the rest is still infeasible. One solve per rule."""
    kept = list(rules)
    for name in rules:
        trial = [n for n in kept if n != name]
        if oracle.infeasible(trial):
            kept = trial
    return kept
```

The filter tries the rows in the order it is given them. Here it runs in the order the model builds
them (`once_P001` first, `force_P032_2028` last) and in the reverse order:

```text
70 rows, from once_P001 to force_P032_2028
deletion, build order:  70 solves -> ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028']
deletion, reversed   :  70 solves -> ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']
```

Two different IISs, from the same filter on the same model. Both cost 70 solves, one per row. The
order chooses between them: a row is dropped whenever the rest is still infeasible without it, and
early in the pass the rest still holds every other conflict. So the rows tested first are the most
likely to be dropped, and the conflict that survives is the one whose rows come last. In build
order the board's overrides come last, and the override conflict survives. In reverse they come
first and are dropped, because P017's crew conflict still holds without them.

That makes the order a tool. Test the rows you would rather not blame first, and the rows you want
a planner to look at last.

## The Additive Filter Builds a Conflict From Nothing

The **additive filter** works the other way round. Start with an empty conflict. Add rows one at a
time until the set turns infeasible: the row that tipped it belongs to the conflict. Start again
from the conflict found so far, and stop when the conflict alone is infeasible:

```python
def additive_filter(oracle: Oracle, rules: list[str]) -> list[str]:
    """Add rules one at a time onto the conflict found so far; the rule that tips the set into
    infeasibility belongs to the conflict. Repeat until the conflict alone is infeasible."""
    conflict: list[str] = []
    while not oracle.infeasible(conflict):
        trial = list(conflict)
        for name in rules:
            if name in conflict:
                continue
            trial.append(name)
            if oracle.infeasible(trial):
                conflict.append(name)
                break
        else:
            raise ValueError("the rules are feasible together: there is no conflict to find")
    return conflict
```

```text
additive, build order: 138 solves -> ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']
```

In build order, the must-do rows come before the crew and override rows, so the first conflict to
close as rows are added is P017's. The filter returns a third answer for the same order. It used
138 solves against the deletion filter's 70, because each of its three rounds scans the rows again
from the start. An additive pass pays off when a conflict closes early in the list, since every
row after that point is never tested.

Each filter's answer is irreducible by construction: the deletion filter keeps a row only when
removing it made the rest feasible, and the additive filter adds only rows that the set needed.
The module's tests check both answers row by row: dropping any one member makes the set feasible.

<!-- practice 1 -->

## Every Conflict, One at a Time

One IIS, fixed, can leave another behind. Gurobi's infeasibility tour shows the loop for this in
its `workforce2` example: find an IIS, remove one of its constraints, look again, until the model is
feasible. Here the row removed is one that planners or finance set:

```python
while oracle.infeasible(active):
    conflict = deletion_filter(oracle, active)
    dropped = next(n for n in conflict if n.startswith(("force_", "budget_", "crews_")))   # a row planners set
    print(f"conflict {sorted(conflict)} -> switch off {dropped}")
    active.remove(dropped)
```

```text
conflict ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028'] -> switch off crews_transmission_2028
conflict ['after_P023_2029', 'budget_2028', 'force_P023', 'force_P032_2028'] -> switch off budget_2028
conflict ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017'] -> switch off crews_transmission_2030
feasible once 3 rows are off; 211 solves in all
```

The Budget Lock scenario has three conflicts, and the first two share three rows. The board's two
overrides, with P023's precedence row, clash with the 2028 transmission crews *and*, separately,
with the locked 2028 budget. Switching off the crew row only uncovers the budget conflict behind it.
Switching off one override instead would have ended both conflicts at once. That is a choice for the
planners, and the message of lesson 9.1.6 gives them what they need to make it. The third conflict
is P017's crews, the one the pre-solve check of lesson 9.1.2 already named.

## computeIIS Counts Variable Bounds as Members

Now gurobipy. `convert.to_gurobi` copies the MathOpt model row for row and name for name: the same
80 variables and 70 rows, well under the size-limited license. Each copy runs in a Gurobi
environment that prints nothing, so no license or machine detail reaches the output.
`computeIIS` marks each member with an attribute: `IISConstr` on rows, `IISLB` and `IISUB` on
variable bounds. `IISMinimal` says whether the result is irreducible:

```python
    rows = sorted(c.ConstrName for c in g.getConstrs() if c.IISConstr)
    lower = [v.VarName for v in g.getVars() if v.IISLB]
    upper = [v.VarName for v in g.getVars() if v.IISUB]
```

```text
MILP, computeIIS: minimal True, 6 rows, 24 lower bounds, 1 upper bounds
   rows: ['after_P023_2029', 'budget_2028', 'crews_distribution_2030', 'force_P023', 'force_P032_2028', 'must_P039']
   upper bounds: ['x_P022_2028'] | lower bounds, e.g.: ['x_P001_2028', 'x_P002_2028', 'x_P004_2028']
```

Gurobi's IIS has six rows, two more than the filter's budget conflict: P039's must-do row and the
2030 distribution crews. It also has 25 variable bounds. The filter treats all 160 bounds as a
fixed background and so can only trade rows. Gurobi treats bounds as members it may leave out, so
its IIS can drop a bound and keep a row instead. Both answers are irreducible, each by its own
rules. To make Gurobi choose among rows only, as the filter does, force every bound into the IIS.
The **force attributes** take 1 (always in), 0 (always out) or −1 (Gurobi decides, the default):

```python
def bounds_in(g) -> None:
    """Force every variable bound into the IIS, so that it chooses among rows only."""
    for v in g.getVars():
        v.IISLBForce = 1
        v.IISUBForce = 1
```

```python
    g.getConstrByName(name).IISConstrForce = force
```

```text
bounds forced in: ['after_P023_2029', 'budget_2028', 'force_P023', 'force_P032_2028']
bounds in, budget_2028 out: minimal True, ['crews_transmission_2030', 'crews_transmission_2031', 'must_P017']
bounds in, crews_transmission_2028 in: minimal True, ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028']
```

With the bounds forced in, Gurobi returns the four-row budget conflict that the filter's loop found
second. Forcing `budget_2028` out sends it to P017's conflict. Forcing `crews_transmission_2028` in
gives the crew conflict. Each of the three conflicts the loop found can be had from Gurobi by saying
which rows to keep or exclude. Gurobi's reference warns that forcing too much out can leave a set
that is not infeasible at all, and then `computeIIS` raises an error.

Lesson 5.3.3 said that a binary's bounds never take part in an IIS, yet the IIS above lists 25
bounds of 0-1 variables. Both are true, because the variable *type* decides. Gurobi's attribute
reference says the bounds of a `GRB.BINARY` variable are implicit in its type and never take part
in an IIS. MathOpt has no binary type: a 0-1 decision is an integer variable with bounds 0 and 1,
and `convert.to_gurobi` copies it as `GRB.INTEGER` with those bounds, which Gurobi treats as bounds
like any other. Retyping the same variables as binary takes the bounds out of the IIS:

```python
for v in binary.getVars():
    v.VType = GRB.BINARY                                     # the same variables, typed binary
```

```text
typed BINARY: 4 rows, 0 lower bounds, 0 upper bounds, ['after_P023_2029', 'budget_2028', 'force_P023', 'force_P032_2028']
```

With no bound left to trade, Gurobi returns the same four-row budget conflict as with every bound
forced in. So a rule written as a bound on a binary can never be named by Gurobi's IIS, and a rule
written as a bound on a 0-1 integer is named only as a variable's bound, not as the rule.

## Pyomo: write_iis Asks Gurobi, the MIS Tool Solves the LP Relaxation

Pyomo has two tools, and they work differently. `write_iis(model, file, solver="gurobi")` hands the
model to Gurobi's persistent interface, calls `computeIIS` and writes the IIS to an `.ilp` file
(CPLEX and Xpress are the other choices). `compute_infeasibility_explanation(model, solver)` is a
filter of its own. First it gives every row and bound an elastic variable (lesson 9.1.4) and
collects what had to bend. Then it runs a deletion filter over those rows. It takes any solver;
here it gets HiGHS. Both run on `convert.to_pyomo`'s copy, where each row is `rows[<name>]`:

```python
    with tempfile.TemporaryDirectory() as folder, quiet():
        path = write_iis(model, os.path.join(folder, "lock.ilp"), solver="gurobi")
```

```python
            compute_infeasibility_explanation(model, highs, logger=log)
```

```text
budget-lock: write_iis (Gurobi) rows ['rows(after_P023_2029)', 'rows(budget_2028)', 'rows(crews_distribution_2030)', 'rows(force_P023)', 'rows(force_P032_2028)', 'rows(must_P039)']
budget-lock: MIS tool (HiGHS), 30 solves: ['constraint: rows[force_P032_2028]', 'constraint: rows[force_P023]', 'constraint: rows[after_P023_2029]', 'constraint: rows[crews_transmission_2028]'] + 7 lower bounds
crew-cut: write_iis (Gurobi) rows ['rows(crews_transmission_2030)', 'rows(crews_transmission_2031)', 'rows(must_P017)']
crew-cut: MIS tool (HiGHS), 1 solves: ['raised: Found model GridCap_small_crew-cut to be feasible!']
```

`write_iis` returns Gurobi's six-row IIS, the same as gurobipy's default, since it makes the same
call. The MIS tool returns the four-row crew conflict, plus seven variable lower bounds, in 30 solves. Then
comes the warning in the last line. "crew-cut" is the Budget Lock's crew cut alone, P017's conflict,
which the MILP cannot meet. The MIS tool declares it **feasible**.

The reason is in the tool's source (`pyomo/contrib/iis/mis.py`). Before it starts, it turns every
variable bound into a row and sets every variable's domain to the reals. The tool works on the
**LP relaxation**, where integrality is gone. P017's conflict exists only for integers: with
$`x_{\text{P017},2030} = x_{\text{P017},2031} = 0.5`$, each year needs 6.5 crew-months against 12,
and the relaxation is happy. gurobipy confirms the tool's other answer is an LP answer. The IIS of
the relaxed model (`model.relax()`, every integer variable made continuous) matches the MIS tool's,
row for row:

```text
LP relaxation, computeIIS: ['after_P023_2029', 'crews_transmission_2028', 'force_P023', 'force_P032_2028'] + 7 lower bounds
```

So for a MIP, an LP-based tool finds only the conflicts that survive relaxation, and can call a
MIP feasible when it is not. Use it on an LP, or as a first pass. For a MIP, use a filter whose
oracle solves the MIP, as `filters.Oracle` does, or a MIP-aware IIS like Gurobi's. Pyomo's
documentation adds that the MIS tool is meant for IPOPT, logs its findings rather than returning
them, and that its tolerance is whatever the solver uses.

<!-- practice 2 -->

## Summary

- **An IIS is one conflict: irreducible, but neither unique nor the smallest.** The Budget Lock
  scenario has three conflicts among its rows alone.
- **The deletion filter keeps the conflict it tests last.** One solve per row (70). The order
  picks which conflict survives, so put the rows you want named last.
- **The additive filter builds a conflict from nothing.** 138 solves here, and cheaper when a
  conflict closes early in the list.
- **Every conflict, one at a time:** find one, switch off one of its rows, look again. Three
  conflicts, 211 solves.
- **`computeIIS` counts variable bounds as members.** Its default IIS had six rows and 25 bounds.
  With every bound forced in (`IISLBForce`, `IISUBForce`), it chose among rows only, and
  `IISConstrForce` picked the conflict. The bounds of a variable typed `GRB.BINARY` never take
  part; MathOpt's 0-1 integers, copied as `GRB.INTEGER`, do.
- **Pyomo's `write_iis` asks Gurobi. Its MIS tool solves the LP relaxation**, so it missed P017's
  integer conflict and declared that scenario feasible.

## Reference

| Tool (runner versions) | Call | Works on | Here |
| --- | --- | --- | --- |
| MathOpt | `mathopt.compute_infeasible_subsystem(model, solver)` | Gurobi only | refused or not loadable (lesson 4.3.5) |
| MathOpt + filter | `filters.deletion_filter`, `additive_filter` | the MIP, with any solver | rows only, bounds held fixed |
| gurobipy | `m.computeIIS()`; `IISConstr`, `IISLB`, `IISUB`, `IISMinimal` | the MIP | rows and bounds (never a `GRB.BINARY` variable's bounds) |
| gurobipy | `IISConstrForce`, `IISLBForce`, `IISUBForce` = 1, 0, −1 | | steer which IIS |
| gurobipy | `m.relax()` then `computeIIS()` | the LP relaxation | |
| Pyomo | `write_iis(m, "x.ilp", solver="gurobi")` | the MIP, via Gurobi, CPLEX or Xpress | file with the IIS |
| Pyomo | `compute_infeasibility_explanation(m, solver)` | the LP relaxation | logs repairs and an MIS |

| Filter | Solves | Returns |
| --- | --- | --- |
| deletion | one per row | the conflict among the rows tested last |
| additive | up to one per row per member found | the conflict that closes first |

**Further reading:** OR-Tools,
[MathOpt](https://developers.google.com/optimization/math_opt) (infeasibility analysis among the
advanced features, Gurobi only) and the docstring of `compute_infeasible_subsystem` in
[`solve.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/solve.py).
Gurobi, [`Model` reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html)
(`computeIIS`, the force attributes, not necessarily the smallest IIS),
[variable attributes](https://docs.gurobi.com/projects/optimizer/en/current/reference/attributes/variable.html)
(`IISLB` and `IISUB`: a binary variable's bounds are implicit in its type and never in an IIS),
[Parameters reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`IISMethod`, including method 3, the IIS of the LP relaxation) and the
[infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html)
(`workforce1` and `workforce2`). Pyomo,
[Infeasibility Diagnostics](https://pyomo.readthedocs.io/en/stable/explanation/analysis/iis.html)
(`write_iis`, the MIS tool and its origin in Chinneck's CPAIOR 2007 infeasibility tutorial), and the
tool's source, `pyomo/contrib/iis/mis.py` in Pyomo 6.10.

## Challenges

1. Run the deletion filter with the must-do rows moved to the end of the list. Predict which of
   the three conflicts it returns.
2. In the "every conflict" loop, switch off an override (`force_P023`) whenever a conflict has one.
   How many conflicts does the loop report now?
3. Set Gurobi's `IISMethod` to 3 on the MILP. Predict, from this lesson's last output, which rows
   it returns.

## Design Note: Hold the Bounds, Filter the Rules

`filters.Oracle` switches rows on and off but never touches a variable's bounds or integrality.
That choice sets the vocabulary of the answer. Every member of the IIS is a row with a name a planner
wrote (a budget, a crew cap, an override), never "x_P036_2027 ≥ 0", which no planner can act on.
Gurobi's default IIS is just as correct and harder to explain: 25 of its 31 members are bounds
(of 0-1 variables typed integer; typed binary, they could not be members).
When the IIS will be shown to people, pick the members it may contain before you compute it, as
`IISLBForce` and `IISUBForce` do in gurobipy.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**filters_lock.py.** The deletion filter in two orders, the additive filter, and the loop over
every conflict (*The Deletion Filter*, *The Additive Filter*, *Every Conflict*). *Try:* Run the
additive filter on the reversed order. Predict its number of solves.

- Program: [filters_lock.py](src/filters_lock.py)

**gurobi_iis.py.** `computeIIS` on the MILP, with every bound forced in, steered with
`IISConstrForce`, with the variables typed binary, and on the LP relaxation (*computeIIS Counts
Variable Bounds*, *Pyomo*). It
needs the license the runner mounts. *Try:* Force `must_P039` out. Predict whether the default IIS
changes.

- Program: [gurobi_iis.py](src/gurobi_iis.py)

**pyomo_iis.py.** `write_iis` and `compute_infeasibility_explanation` on the Budget Lock scenario
and on its crew cut alone (*Pyomo*). *Try:* Run the MIS tool on the Budget Lock scenario with
P032's override removed. Predict what it reports.

- Program: [pyomo_iis.py](src/pyomo_iis.py)

The filters, the model and the converters are libraries.

- Library: [filters.py](src/filters.py)
- Library: [convert.py](src/convert.py)
- Library: [lock_model.py](src/lock_model.py)
