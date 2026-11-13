# 7.1.3 The Planning Cycle: Initial, Pre-Opt, Post-Opt, Budget Lock

A capital plan is not solved once. GridCap's planners load the candidate list, check it, optimize
it, look at the result, argue about it, change a budget or force a project in, optimize again, and
finally freeze one plan that goes to finance and into the rate case. Along the way finance asks
"what if 2029 has $2,760k less?", and the answer has to sit beside the base plan, not replace it.
A CIPT (lesson 7.1.1) names the stages of this cycle Initial, Pre-Opt, Post-Opt and Budget Lock,
and it needs a workflow that can create, copy and optimize scenarios across them, with iterative
and ad hoc reruns and manual overrides. This lesson runs one full cycle on GridCap small
and states the rules that keep it trustworthy.

GridCap is a fictional utility, generated for this course. The four stage names are the ones such a
tool uses; what each stage allows below is this course's reading of them, which a real CIPT
would write down in its own requirements. The cycle is the domain side of section 12, where
lessons 12.1.1 and 12.1.3 build it as a service.

Two words first. A **scenario** is one named set of planning inputs: the portfolio, the budgets,
the floors, and any overrides. A **run** is one optimization of one scenario, with its result.

## A Plan Moves Through Four Stages, and Each Stage Decides Who May Change What

The stages answer one question each: what may be changed now, and by whom.

| Stage | What happens | What may change |
| --- | --- | --- |
| **Initial** | the candidate list, budgets and commitments arrive from the fleets and finance, and the data is checked | the inputs, freely |
| **Pre-Opt** | planners adjust the scenario before optimizing: budgets to compare, projects forced in or out | the inputs, by planners |
| **Post-Opt** | the run's plan is read, compared with other scenarios and explained | nothing in place: a change sends the scenario back to Pre-Opt and needs a rerun |
| **Budget Lock** | one plan becomes the plan of record, the one finance and the regulator see | nothing; a change is a new scenario |

`planning_cycle.py` takes GridCap's base scenario through the first three stages. In Initial it
runs two data checks before any solve (each must-do fits the budgets in some start year; no region
floor exceeds everything the region asks for), the cheap prechecks of lessons 6.5.1 and 6.5.5:

```text
[Initial    ] base      snapshot b191e84b9365  checks: no problem found
[Pre-Opt    ] base      budgets [8890, 8120, 8760, 8610, 7850], overrides none
[Post-Opt   ] base      OPTIMAL  NPV $24,260k  funded 27 of 40
```

The checks pass, the planners add no override, and the run funds 27 projects for an NPV of
$24,260k, the plan of section 6. The word **snapshot** in the first line is the subject of the
next section.

Why make the stages explicit at all, rather than letting anyone edit and rerun at will? Because
each group in lesson 7.1.4 needs to know which plan it is looking at. A finance analyst who reads
the spend of a plan that a planner has since edited is reading a plan that no longer exists.

## A Scenario Is a Copy With Its Own Snapshot, Never an Edit of Another Scenario

Finance asks what a smaller 2029 envelope, $6,000k instead of $8,760k, would do. The wrong answer
is to edit the base scenario's budget and rerun: the base plan, which planners are still reviewing,
would be gone. The right answer is a **copy**: a new scenario that starts from the base's inputs,
records where it came from, and is changed on its own.

To tell scenarios and runs apart with certainty, each scenario has a **snapshot** id: the sha256
hash of its inputs written out in one canonical form (lesson 12.2.3 covers content hashes). Equal
inputs give the same id; any change to a budget, a floor, an override or a solver setting gives a
different one. `cycle_model.py` computes it from everything the model is built from:

```python
    def inputs(self) -> dict:
        """Everything the model is built from, in a JSON-ready form."""
        return {"portfolio": self.portfolio.content_hash(),
                "budget": {str(y): v for y, v in sorted(self.budget.items())},
                "floor": dict(sorted(self.floor.items())),
                "force_in": sorted(self.force_in), "force_out": sorted(self.force_out),
                "settings": SETTINGS}

    def snapshot(self) -> str:
        """sha256 of the canonical inputs: equal inputs give the same id, any change gives another."""
        text = json.dumps(self.inputs(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

Two details make the id trustworthy. The portfolio enters through its own content hash
(GridCap's `Portfolio.content_hash()`), so a change to any project's cost or window changes the
snapshot too. And `sort_keys=True` with fixed separators means the same inputs always produce the
same text, whatever order a dictionary happened to be built in. The solver settings are part of
the inputs, because the same data solved with a different gap tolerance can give a different plan.

The copy, its edit and its run:

```text
[Initial    ] cut-2029  copied from base; snapshot b191e84b9365 (same inputs, same id)
[Initial    ] cut-2029  2029 budget $8,760k -> $6,000k; snapshot cf0c4b62ab70
[Pre-Opt    ] cut-2029  checks: no problem found
[Post-Opt   ] cut-2029  OPTIMAL  NPV $23,086k  funded 26
                         base -> cut-2029: dropped ['P001', 'P005', 'P016']; added ['P002', 'P037']; moved ['P008 2031->2029', 'P011 2031->2029', 'P012 2031->2030', 'P021 2029->2028', 'P025 2028->2029', 'P035 2027->2028']
```

The copy starts with the base's snapshot, because its inputs are identical; the budget edit gives
it its own. A copy starts in Initial, like any new scenario, so its changed inputs are checked
before it is optimized. The cut costs $1,174k of NPV ($24,260k less $23,086k), and the **scenario diff** on the
last line is what a planner reads first: which projects were dropped, which were added, and which
moved year. One change is worth spelling out. P001 and P002 are the replace and the repair option
for the same asset, A001 (alternative group G001). With less money in 2029, the plan swaps the
$2,640k replacement for the $460k repair. A cut in one year also moves work in other years: six
projects change start year, some earlier and some later, because the budget rows of all five years
are solved together. Lesson 9.3.3 builds this diff into a report.

<!-- practice 1 -->

## Post-Opt Reads the Plan, and Every Override Sends the Scenario Back for a Rerun

Post-Opt is where planners meet the plan, and they bring knowledge the model does not have. In
GridCap small, the Ridge undergrounding job P024 was not funded; a planner knows that Ridge
customers were promised it, and **forces it in**. An override is a change of inputs like any
other. It goes into the scenario, gives a new snapshot, sends the scenario back to Pre-Opt, and
needs a rerun before anyone may read a plan again:

```text
[Pre-Opt    ] base      planner forces in P024; snapshot 0c172b64f9b3
[Post-Opt   ] base      OPTIMAL  NPV $23,987k  the override costs $273k
                         before -> after override: dropped ['P005', 'P009', 'P016']; added ['P024', 'P037']; moved ['P008 2031->2029', 'P011 2031->2029', 'P018 2030->2031']
```

The override costs $273k of NPV: the same "price it by solving with and without" rule as lesson
6.5.6. It also changes more than P024. Three projects leave the plan, P037 (the other Ridge
undergrounding job) comes in, and three move year. A planner who forced one project in should see
all of that before agreeing to it, which is why the diff is printed with the cost.

What the rule protects against is a plan that no run produced. If a planner could add P024 to the
Post-Opt plan by hand, without a rerun, the plan would overspend: P024 spends $850k in each of two
years, and the base plan leaves at most $150k of any year's budget unspent (lesson 7.1.4 prints
the headroom). Its NPV would also be a number no solver computed. "Every change goes back through the model" is what
keeps a plan feasible and its numbers true.

## Budget Lock Freezes the Plan of Record, and a Change Means a New Scenario

When the planners, finance and management agree, one scenario's latest run becomes the **plan of
record**: the plan that sets next year's spending and supports the rate case. Budget Lock freezes
it. A locked scenario refuses edits; a change after lock needs a copy, which goes through the cycle
again and, if adopted, replaces the plan of record by a decision, not by an edit:

```python
def edit(s: Scenario, **changes) -> None:
    """Change a scenario's inputs. A locked scenario refuses; a solved one goes back to Pre-Opt."""
    if stage[s.name] == "Budget Lock":
        raise PermissionError(f"{s.name} is locked; copy it to change it")
    for key, value in changes.items():
        setattr(s, key, value)
    if stage[s.name] == "Post-Opt":
        stage[s.name] = "Pre-Opt"
```

```text
[Budget Lock] base      plan of record: snapshot 0c172b64f9b3, NPV $23,987k
[Budget Lock] base      edit refused: base is locked; copy it to change it
[Budget Lock] base      rerun of the locked snapshot: same plan True, same NPV True
```

The last line is the property a regulator will test in lesson 7.1.4: run the locked snapshot
again and get the same plan. Here it held, on one machine with the same OR-Tools and HiGHS and the
settings recorded in the snapshot. That is evidence for this run, not a guarantee. A snapshot fixes
the inputs, but solver version, thread count and time limits can still change the result when a
model has several optimal plans or stops before proving optimality; lessons 4.6.3, 10.2.1 and
10.2.2 measure when reruns repeat and when they do not. A locked plan of record therefore keeps its
plan as well as its snapshot, so that nobody has to re-derive it.

<!-- practice 2 -->

## The Model

The planning model every scenario of this lesson builds (`cycle_model.build`), in one place. It is
the multi-period model of lessons 6.4.1 to 6.4.3 and 6.5.1, with the region floors of lesson 6.5.5
and the planner overrides of this lesson.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`F^{+} \subseteq P`$ the projects a
planner forces in and $`F^{-} \subseteq P`$ those forced out (disjoint, and $`F^{-} \cap M =
\emptyset`$); $`\mathcal{G}`$ the alternative groups; $`C \subseteq P`$ the child projects, with
parent $`p(c)`$ and lag $`L_c`$ years; $`R`$ the regions, with $`P_r \subseteq P`$ the projects
in region $`r`$.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k), and
$`\text{capex}_i = \sum_k c_{i,k}`$; $`B_y`$, the budget of year $`y`$ ($k); $`F_r`$, the least
region $`r`$ must receive over the plan ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$. We write $`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ and
$`\text{by}(i, t) = \sum_{s \in T_i,\, s \le t} x_{i,s}`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus (M \cup F^{+} \cup F^{-}) && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\text{started}(i) &= 1 && \forall i \in F^{+} \setminus M && \text{(in}_i) \quad \leftarrow \text{this lesson} \\
\text{started}(i) &= 0 && \forall i \in F^{-} && \text{(out}_i) \quad \leftarrow \text{this lesson} \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{by}(c, t) &\le \text{by}(p(c),\, t - L_c) && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\textstyle\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\textstyle\sum_{i \in P_r} \text{capex}_i\, \text{started}(i) &\ge F_r && \forall r \in R && \text{(floor}_r)
\end{aligned}
```

| Label | Row name in `cycle_model.py` |
| --- | --- |
| once$`_i`$, must$`_i`$, in$`_i`$, out$`_i`$ | `once_P001`, `must_P017`, `in_P024`, `out_P032` |
| alt$`_g`$ | `alt_G030` |
| after$`_{c,t}`$ | `after_P016_2030` |
| budget$`_y`$ | `budget_2029` |
| floor$`_r`$ | `floor_Ridge` |

A forced-in project is a row on $`\text{started}(i)`$, so the solver still picks its start year;
lesson 6.5.6 writes an override that also fixes the year as bounds on the start variables. The
floor rows use the whole capex because every GridCap window ends the work inside the plan.

## Summary

- **A plan moves through four stages, and each stage decides who may change what.** Initial
  checks the data, Pre-Opt sets up the scenario, Post-Opt reads the run, Budget Lock freezes the
  plan of record.
- **A scenario is a copy with its own snapshot, never an edit of another scenario.** The snapshot
  is a hash of every input, settings included; equal inputs give equal ids.
- **Post-Opt reads the plan, and every override sends the scenario back for a rerun.** Price the
  override and show the diff it causes.
- **Budget Lock freezes the plan of record, and a change means a new scenario.** Keep the locked
  plan with its snapshot; a rerun that repeats is evidence, not a guarantee.

## Reference

| Stage | Entered when | Leaves when |
| --- | --- | --- |
| Initial | a scenario is created or copied | its data checks pass |
| Pre-Opt | the checks pass, or an input of a Post-Opt scenario is edited | a run finishes |
| Post-Opt | a run finishes | an input is edited (back to Pre-Opt) or the plan is locked |
| Budget Lock | the plan is adopted as the plan of record | never; changes go to a copy |

| Term | Meaning |
| --- | --- |
| scenario | a named set of inputs: portfolio, budgets, floors, overrides, solver settings |
| run | one optimization of one scenario |
| snapshot | sha256 of a scenario's canonical inputs |
| scenario diff | projects dropped, added and moved between two plans |
| plan of record | the locked plan that finance and the regulator see |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt),
which separates the model from the solver it is sent to, the property that lets one scenario be
rebuilt and rerun unchanged; the OR-Tools MathOpt sample
[`integer_programming.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py),
which checks the termination reason before reading a plan, as `optimize` does; J. Lazar,
[*Electricity Regulation in the US: A Guide*, 2nd ed.](https://www.raponline.org/knowledge-center/electricity-regulation-in-the-us-a-guide-2/)
(Regulatory Assistance Project, 2016), section 8.2 (historical and future test years, the budgets
a locked plan feeds).

## Challenges

1. Copy the base scenario and force P032 out. Predict whether the NPV drops by more or less than
   P032's own NPV of $3,678k, and why it could be either.
2. In `planning_cycle.py`, rerun the cut scenario with the budget set back to $8,760k. Predict its
   snapshot.
3. Add a stage check to `edit` so that an Initial scenario whose checks fail cannot move to Pre-Opt.

## Design Note: The Stage Belongs to the Scenario, Not to the Program

`planning_cycle.py` keeps the stages in a dictionary beside the scenarios, which is enough to show
the rules. A real tool stores the stage with the scenario, next to its snapshot, its runs and who
changed what (lesson 12.1.2 adds the audit trail, and 12.1.3 the states and locking). Then "who may
change what" is a check the service makes on every request, not a habit people are trusted to keep.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**planning_cycle.py.** Takes GridCap's base scenario from Initial to Budget Lock, with a copied
scenario for a budget cut, a planner override and a rerun of the locked snapshot (every section of
this lesson). *Try:* Force in P037 instead of P024. Predict whether it costs more or less than
$273k.

- Program: [planning_cycle.py](src/planning_cycle.py)

**cycle_model.py.** The scenario record, its snapshot, and the planning model of *The Model* above.
It runs nothing itself.

- Library: [cycle_model.py](src/cycle_model.py)
