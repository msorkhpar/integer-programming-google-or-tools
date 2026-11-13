# 4.1.3 Choosing an API for a Problem

By the end of section 4, GridCap's planning service will use five parts of OR-Tools: MathOpt for the
project selection, CP-SAT for the vegetation crews' schedule, the assignment solver for crews to
sites, a minimum-cost flow for shipping spare transformers, and the routing library for inspection
routes. Nobody picked those by taste. Each problem statement carried the facts that decide it, and
this lesson turns those facts into a short procedure you can run on any statement, in an interview or
on the job.

The procedure asks five questions in order, and each heading below is one of them. The evidence for
each comes from a program. Some of it was measured in lessons 4.1.1 and 4.1.2; most of it is
measured in lessons later in this section, which the page names as it goes, so read those as
pointers to where the measurement is made, not to lessons you have already done. The one new
program takes lesson 4.1.1's crew assignment and adds two rules to it, one that the assignment solver can take and one
that it cannot. GridCap is a fictional utility; its crews, sites and hours here are invented.

## The Model

Lesson 4.1.1's crew assignment, with the two new rules marked.

**Sets.** $`K`$ = {Ridge, Valley, Coast, Plains}, the crews; $`S`$ = {S1, S2, S3, S4}, the
substations; $`F \subseteq K \times S`$, the pairs a crew is not cleared for (new: $`F`$ = {(Ridge,
S2)}).

**Parameters.** $`h_{k,s}`$, the travel hours for crew $`k`$ to reach site $`s`$ (whole hours);
$`T = 9`$, the hours the shared truck can give the Coast and Plains crews together (new).

**Variables.** $`y_{k,s} \in \{0, 1\}`$ for every $`(k, s) \notin F`$: 1 if crew $`k`$ goes to
site $`s`$. A pair in $`F`$ gets no variable at all.

```math
\begin{aligned}
\min \;& \sum_{(k,s) \notin F} h_{k,s}\, y_{k,s} \\
\text{s.t. } & \sum_{s : (k,s) \notin F} y_{k,s} = 1 && \forall k \in K && \text{(one\_site}_k) \\
& \sum_{k : (k,s) \notin F} y_{k,s} = 1 && \forall s \in S && \text{(one\_crew}_s) \\
& \sum_{k \in \{\text{Coast}, \text{Plains}\}} \; \sum_{s : (k,s) \notin F} h_{k,s}\, y_{k,s} \le T && && \text{(truck, new)}
\end{aligned}
```

## Does It Move Vehicles Between Places? Then the Routing Library

A problem whose decisions are **routes** (which vehicle visits which stops, in which order, starting
and ending at a depot) goes to the routing library first, and stays there when rules pile on. The
OR-Tools routing guide lists the variants it is built for: several vehicles, vehicle capacities, time
windows at each stop, resource limits at the depot, and stops that may be dropped at a penalty. Each
of those is a parameter or a "dimension" of the routing model (taught from lesson 4.8.1 on, at the
end of this section), not a new formulation.

The price, from lesson 4.1.1: the routing library searches, and reports `ROUTING_SUCCESS` for a good
route, not a proof of the best one. Accept that for routes: the routing library takes their rules
as parameters of one model, where a MILP would need a variable for every arc and every vehicle and
rows to keep each route in one piece. Do not stretch "routing" to everything with an order in it or a truck in it, though.
The order of jobs on one machine or one crew has no travel between places as its decision, and goes
to CP-SAT below. And a problem that decides only how much moves along each road, with no vehicle's
sequence of stops in it, is a flow (the next question), even when trucks carry the loads. Crews
that go from one circuit's job to the next are the first case when the statement gives job lengths
and an order but no travel between circuits: the decision is each job's day, and the table below
sends the vegetation crews' schedule across circuits to CP-SAT.

## Is It Exactly an Assignment, a Flow or a Knapsack? Then Its Special Solver, Until One Rule Breaks the Shape

Lesson 4.1.1 showed the special-purpose solvers giving the general models' answers with less code. The
assignment solver documentation adds that it can be faster than the MIP or CP-SAT solver on the
problem it was built for. But each takes one shape, and only that shape. The program here puts two
new rules on the crew assignment and asks both the assignment solver and CP-SAT. A pair a crew may
not use is easy for the assignment solver: never add that arc. Its shape is a one-to-one pairing,
the rows $`\text{one\_site}_k`$ and $`\text{one\_crew}_s`$ above: no worker gets two tasks and no
task two workers, so jobs that one crew does in turn are not an assignment.

```python
def assignment_solver(forbidden: set[tuple[int, int]]) -> str:
    solver = linear_sum_assignment.SimpleLinearSumAssignment()
    for k in K:
        for s in S:
            if (k, s) not in forbidden:                 # a pair it may not use is an arc never added
                solver.add_arc_with_cost(k, s, hours[k][s])
    if solver.solve() != solver.OPTIMAL:
        return "no assignment"
    return show(solver.optimal_cost(), [solver.right_mate(k) for k in K])
```

The truck rule ties two crews' hours together, so it is a row of the model, and only a general model
has rows:

```python
    if truck_limit is not None:                                             # truck: Coast + Plains hours
        model.add(sum(hours[k][s] * y[k, s] for (k, s) in y if crews[k] in ("Coast", "Plains")) <= truck_limit)
```

```text
as in lesson 4.1.1
  assignment solver: 15 hours  Ridge->S2, Valley->S1, Coast->S3, Plains->S4
  CP-SAT:            15 hours  Ridge->S2, Valley->S1, Coast->S3, Plains->S4
Ridge not cleared for S2
  assignment solver: 18 hours  Ridge->S4, Valley->S1, Coast->S3, Plains->S2
  CP-SAT:            18 hours  Ridge->S4, Valley->S1, Coast->S3, Plains->S2
and Coast + Plains share a truck: at most 9 hours between them
  CP-SAT:            19 hours  Ridge->S1, Valley->S3, Coast->S2, Plains->S4
  assignment solver: its only ways to add data are add_arc_with_cost and add_arcs_with_cost
```

With the forbidden pair, both still agree (18 hours). The 18-hour plan gives Coast and Plains 4 + 6 =
10 hours, over the truck's 9, so the truck rule must change it, and CP-SAT finds the 19-hour plan
that keeps it. The assignment solver has no way to be asked: its only inputs are arcs with costs, one
pair at a time, and the truck rule is about two pairs at once.

That is the test for every special-purpose solver. **Can each rule be said in that solver's own
inputs?** For the assignment solver, a rule about one (worker, task) pair can (drop or price the arc);
a rule that couples pairs cannot. For a flow solver, capacities, costs, supplies and demands can; "this
arc is used only if that one is" cannot. For the knapsack solver, more capacity rows can (lesson
4.1.1); must-do items, alternatives and parent links cannot. One rule that cannot be said, and the
problem is a general model; the next two questions say which kind.

## Are There Fractional Amounts or Dual Prices? Then a General Model in MathOpt

A general model now goes to MathOpt or CP-SAT. Two facts send it to **MathOpt**, with HiGHS or SCIP
as the solver, whatever else it has:

- **A continuous variable**: tons, megawatts, dollars that may be fractional. CP-SAT has no continuous
  variable (lesson 4.4.1), and handed one through MathOpt it rounds it and still reports `OPTIMAL`
  (lesson 4.2.3, later in this section, measures 22,532 against the true 23,669.5). Rules of logic do
  not change this: MathOpt states "if this, then that" with indicator constraints or big-M rows. An
  indicator constraint is a row that must hold only when a chosen binary variable is 1 (lesson 4.3.1,
  later in this section); a big-M row is an ordinary linear row with a large constant $`M`$ times a
  binary in it, so that the row is switched off when the binary is 0 (lesson 6.2.1, in section 6).
- **Dual values**: a shadow price for the budget, a reduced cost for a project. Only an LP has them,
  and among MathOpt's solvers only GLOP, PDLP and HiGHS return them (measured in lesson 4.2.3, later in this
  section); CP-SAT returns none.

The OR-Tools MIP guide gives the same split from its side: for problems with both integer and
continuous variables it recommends a MIP solver (it names SCIP), and for integer-only problems,
CP-SAT. This course uses HiGHS as its default MIP solver and SCIP as the second opinion, both through
MathOpt.

## Are There Intervals, Sequences or Dense Logic Over Integers? Then CP-SAT

An integer-only general model goes to **CP-SAT** when it is mostly logic: tasks with start times and
durations that may not overlap, crews shared over time, "this job before that one, or the other way
round", many if-then rules. Lesson 4.4.4, later in this section, measures why: a sequencing model written for HiGHS with big-M
disjunctions kept a bound of 0 after 10,000 nodes on 10 circuits, while CP-SAT proved every optimum
in its limit. CP-SAT also has the vocabulary: interval variables, `add_no_overlap` and
`add_cumulative` (lessons 4.5.1 and 4.5.2), which the OR-Tools job shop example uses, and which MathOpt does not
have.

All of that requires whole numbers. Data with decimals is scaled first (lesson 4.4.3); a quantity
that is truly continuous sends the model back to the previous question.

## Everything Else Starts in MathOpt, and pywraplp Is for Code You Inherit

What is left is a general integer model with no special shape, no continuous part and no dense logic:
GridCap's project selection is the example. It is a capital budget that is not a knapsack: its
must-do projects, alternatives and parent links are the rules the knapsack solver cannot take
(question 2 and lesson 4.1.1). Lesson 4.4.4, later in this section, finds that on a plain selection both
HiGHS and CP-SAT prove the same optimum, and that on GridCap medium's large ten-year selection HiGHS
ends closest to proven. **Start it in MathOpt**: the model stays solver-free, so trying CP-SAT on it later
is one argument (lesson 4.2.3), and that measurement, on your own instances, settles it.

Two APIs are left off the procedure on purpose:

- **The linear solver wrapper (`pywraplp`)** does the same job as MathOpt with an older design: the
  solver is fixed when the model is created, and its LP solvers drop integer variables silently
  (lesson 4.1.2). New code goes to MathOpt; a `pywraplp` model you inherit is read, tested and
  migrated (lessons 4.7.1 and 4.7.2). Migrated means moved to MathOpt, where the procedure starts
  every general model, not ported to a special solver or another API.
- **Gurobi** is a backend, not an API, and in this course's runner neither OR-Tools API can load it
  (lesson 4.1.2). When a problem needs Gurobi, use `gurobipy` (section 5, from lesson 5.3.1).

## The Procedure, in Order

The five questions, in the order to ask them. The first that says yes decides:

1. **Vehicles moving between places?** The routing library.
2. **Exactly an assignment, a flow or a knapsack, with every rule in that solver's inputs?** The
   assignment, flow or knapsack solver.
3. **A continuous amount, or dual prices wanted?** MathOpt, with HiGHS or SCIP (GLOP or HiGHS for
   LP duals).
4. **Intervals, sequencing or dense logic, all integer?** CP-SAT.
5. **Otherwise:** MathOpt, measured against CP-SAT when it matters.

Run on section 4's own GridCap problems, it gives the plan the opening named:

| GridCap problem | Deciding fact | API | Where taught |
| --- | --- | --- | --- |
| inspection crews visiting substations with time windows | vehicles moving between places | routing | the module *OR-Tools routing* |
| crews to sites, one each, least travel | exactly an assignment | `SimpleLinearSumAssignment` | lesson 4.7.4 |
| spare transformers from depots to substations | exactly a min-cost flow | `SimpleMinCostFlow` | lesson 4.7.3 |
| vegetation crews' schedule across circuits | intervals and no-overlap | CP-SAT | the module *CP-SAT scheduling* |
| project selection under budgets and rules | none of the above | MathOpt with HiGHS | the modules *MathOpt core* and *MathOpt advanced* |

Two warnings about the order. It matters: an assignment with a rule that couples two pairs fails
question 2 and is decided further down, and a schedule with a fractional quantity stops at question 3,
before it reaches CP-SAT. And it is a starting point, not a verdict: question 5 already says to
measure, and lesson 4.4.4, later in this section, shows the same model can favor either solver depending on its size and
its rows.

<!-- practice 1 -->

## Summary

- **Routes go to the routing library**, which takes capacities, time windows and droppable stops as
  parameters and returns good routes rather than proven ones.
- **A problem that is exactly an assignment, flow or knapsack goes to its special solver**, until one
  rule cannot be said in that solver's inputs; the assignment solver took a forbidden pair, and could
  not take a rule coupling two crews.
- **Continuous amounts or dual prices send a general model to MathOpt**, because CP-SAT rounds
  continuous variables and returns no duals.
- **Intervals, sequencing and dense logic over integers send it to CP-SAT.**
- **Everything else starts in MathOpt**; `pywraplp` is for code you inherit, and Gurobi goes through
  `gurobipy`.

## Reference

| Fact in the problem statement | API | Why (evidence) |
| --- | --- | --- |
| vehicles, stops, depot, routes | routing library | built for it; good routes, not proofs (4.1.1) |
| one-to-one pairing at least cost, nothing else | `SimpleLinearSumAssignment` | same answer as the MIP, less code (4.1.1) |
| supplies, demands, capacitated arcs, nothing else | `SimpleMinCostFlow`, `SimpleMaxFlow` | the shape it takes (4.1.1, 4.7.3) |
| one or more capacity rows over yes/no items, nothing else | `KnapsackSolver` | same answer as three general models (4.1.1) |
| a rule the special solver's inputs cannot say | a general model | the truck rule (this lesson) |
| fractional quantities | MathOpt with HiGHS or SCIP | CP-SAT rounds them (4.2.3) |
| shadow prices or reduced costs | MathOpt with GLOP or HiGHS, as an LP | only LP solvers return duals (4.2.3) |
| start times, durations, no-overlap, shared crews | CP-SAT | intervals; big-M bounds are weak (4.4.4) |
| many if-then or either-or rules, all integer | CP-SAT | native logic (4.4.2, 4.4.4) |
| a plain selection or other integer model | MathOpt, then measure CP-SAT | both prove the optimum (4.4.4) |
| an existing `pywraplp` model | read it, then migrate to MathOpt | 4.7.1, 4.7.2 |
| "must run on Gurobi" | `gurobipy` | no OR-Tools API loads it in the runner (4.1.2) |

The numbers in the last column name the lesson that shows the evidence. Apart from 4.1.1 and 4.1.2,
each of them comes later in this section.

**Further reading:** [Get Started with OR-Tools for
Python](https://developers.google.com/optimization/introduction/python) (identify the type of
problem first, then choose a solver for it); [Solving a MIP
Problem](https://developers.google.com/optimization/mip/mip_example) (CP-SAT recommended for
integer-only problems, SCIP for problems with continuous variables too); [Solving an Assignment Problem
with the Linear Sum Assignment Solver](https://developers.google.com/optimization/assignment/linear_assignment)
(faster than the MIP or CP-SAT solver on the simple assignment problem, which the general solvers
extend); [Solving an Assignment Problem](https://developers.google.com/optimization/assignment/assignment_example)
(the same assignment as a MIP and in CP-SAT); [Vehicle Routing](https://developers.google.com/optimization/routing)
(the routing variants and their constraints); [The Job Shop Problem](https://developers.google.com/optimization/scheduling/job_shop)
(scheduling with CP-SAT's interval variables and no-overlap); [Network
Flows](https://developers.google.com/optimization/flow) (the flow problems the graph solvers take);
[The Knapsack Problem](https://developers.google.com/optimization/pack/knapsack) (the knapsack
solver's inputs); [MathOpt](https://developers.google.com/optimization/math_opt) (the problem types
MathOpt takes, including continuous variables and indicator constraints); [Advanced LP
Solving](https://developers.google.com/optimization/lp/lp_advanced) (no LP solver is best on every
problem; start with GLOP); [The CP-SAT Primer, introduction (Krupke)](https://d-krupke.github.io/cpsat-primer/)
(MIP solvers' scale against CP-SAT's strength on problems full of logical constraints, and MathOpt as
a modeling layer over both).

## Challenges

1. A warehouse ships pallets from three depots to five substations, at least cost, but each
   substation must be served by one depot only. Run the procedure. Which question decides it, and
   why not question 2?
2. In `side_rule.py`, raise the truck limit until CP-SAT's plan is the 18-hour plan again. What is
   the smallest limit that does it?
3. Write the procedure as a function of a problem's facts. The practice below asks for exactly that;
   try it first on the five GridCap problems of the table.

## Design Note: Name the Deciding Fact in the Code

When you choose an API, write down the fact that chose it, next to the code: "routing: crews drive
between substations", "CP-SAT: crew jobs may not overlap". Requirements move, and the fact is what
tells the next engineer whether the choice still holds. The day a planner adds "Coast and Plains share
a truck" to the crew assignment, the comment "assignment solver: exactly an assignment, nothing else"
says at once that the code must change, which is easier than finding out from a plan that breaks the
new rule.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**side_rule.py.** Lesson 4.1.1's crew assignment with a forbidden pair and a shared-truck rule, in
the assignment solver and in CP-SAT (*Is It Exactly an Assignment*). *Try:* Forbid every site but S4
to the Plains crew as well. Predict both solvers' plans.

- Program: [side_rule.py](src/side_rule.py)
