# 4.1.1 What's in OR-Tools: MathOpt, CP-SAT, the Linear Solver Wrapper, Routing, Graph

GridCap's planning team has three jobs on its desk this week. Finance wants this year's capital
projects picked under the budget. The field manager wants four line crews sent to four substations
with the least total travel. And an inspection crew needs a round trip from the depot through five
substations. Everyone on the team has heard "use OR-Tools" for all three, and the first thing a new
engineer finds is that OR-Tools is not one solver with one way of writing a model. It is a package
of several solvers, each with its own Python API (application programming interface: the classes and
functions you call), built for different kinds of problem.

This lesson opens the package and solves each of the three jobs with the part of OR-Tools built for
it, and the first job with four parts at once, so you can see what each family looks like in code
and what it costs you. Every later module of section 4 takes one family and goes deep; this one is
the map. GridCap is a fictional utility's portfolio, generated for this course, and the crews,
substations and distances below are invented for this lesson.

## The Model

The three jobs, stated before any code. Each is small on purpose: the point is how each API takes
it, not how hard it is.

**Job 1: the budget pick** (GridCap tiny, one period, the budget row only; lesson 4.2.1 adds the
other rules).

**Sets.** $`P`$, the 8 projects of GridCap tiny.

**Parameters.** $`v_i`$, the NPV of project $`i`$ if it starts as early as it can ($k);
$`c_i`$, its capex ($k); $`B = 7{,}390`$, the capital budget ($k).

**Variables.** $`x_i \in \{0, 1\}`$ for every $`i \in P`$: 1 if project $`i`$ is funded.

**Objective and constraint.**

```math
\begin{aligned}
\max \;& \sum_{i \in P} v_i\, x_i \\
\text{s.t. } & \sum_{i \in P} c_i\, x_i \le B && \text{(budget)}
\end{aligned}
```

A model with one row of this kind (pick items, each with a value and a weight, under one capacity)
is a **knapsack problem**, named after packing a bag.

**Job 2: crews to substations.**

**Sets.** $`K`$, the 4 crews; $`S`$, the 4 substations.

**Parameters.** $`h_{k,s}`$, the travel hours for crew $`k`$ to reach site $`s`$ (whole hours).

**Variables.** $`y_{k,s} \in \{0, 1\}`$: 1 if crew $`k`$ goes to site $`s`$.

```math
\begin{aligned}
\min \;& \sum_{k \in K} \sum_{s \in S} h_{k,s}\, y_{k,s} \\
\text{s.t. } & \sum_{s \in S} y_{k,s} = 1 && \forall k \in K && \text{(one\_site}_k) \\
& \sum_{k \in K} y_{k,s} = 1 && \forall s \in S && \text{(one\_crew}_s)
\end{aligned}
```

Pairing each member of one group with exactly one member of another at least total cost is the
**assignment problem**.

**Job 3: the inspection tour.**

**Sets.** $`N = \{0, 1, \dots, 5\}`$, the depot (0) and five substations.

**Parameters.** $`d_{i,j}`$, the road distance from stop $`i`$ to stop $`j`$ (whole km).

**Decision.** For each stop $`i`$, the stop $`\text{next}_i \in N`$ the crew drives to after it.

```math
\begin{aligned}
\min \;& \sum_{i \in N} d_{i,\,\text{next}_i} \\
\text{s.t. } & \text{the links } i \to \text{next}_i \text{ form one tour that leaves the depot, visits every stop once and returns} && \text{(tour)}
\end{aligned}
```

One vehicle, every stop once, shortest round trip: the **traveling salesperson problem** (TSP). It
can be written as a MILP, but the routing library below takes it in this form directly: you give it
the distances, and its decision is the next stop of each stop.

## OR-Tools Is One pip Package Holding Several Separate Solver Families

`pip install ortools` installs one package, and the families live in separate subpackages with
separate Python modules. The program imports the module each family is used through and checks that
the classes this section starts from are there:

```python
FAMILIES = [
    # (family, module to import, names the lessons of section 4 start from)
    ("MathOpt", "ortools.math_opt.python.mathopt", ["Model", "solve", "SolverType"]),
    ("CP-SAT", "ortools.sat.python.cp_model", ["CpModel", "CpSolver"]),
    ("linear solver wrapper", "ortools.linear_solver.pywraplp", ["Solver"]),
    ("routing", "ortools.constraint_solver.pywrapcp", ["RoutingIndexManager", "RoutingModel"]),
    ("graph: max flow", "ortools.graph.python.max_flow", ["SimpleMaxFlow"]),
    ("graph: min-cost flow", "ortools.graph.python.min_cost_flow", ["SimpleMinCostFlow"]),
    ("graph: assignment", "ortools.graph.python.linear_sum_assignment", ["SimpleLinearSumAssignment"]),
    ("knapsack", "ortools.algorithms.python.knapsack_solver", ["KnapsackSolver"]),
]
```

```text
OR-Tools 9.15.6755
family                 import from                                 names
MathOpt                ortools.math_opt.python.mathopt             Model, solve, SolverType
CP-SAT                 ortools.sat.python.cp_model                 CpModel, CpSolver
linear solver wrapper  ortools.linear_solver.pywraplp              Solver
routing                ortools.constraint_solver.pywrapcp          RoutingIndexManager, RoutingModel
graph: max flow        ortools.graph.python.max_flow               SimpleMaxFlow
graph: min-cost flow   ortools.graph.python.min_cost_flow          SimpleMinCostFlow
graph: assignment      ortools.graph.python.linear_sum_assignment  SimpleLinearSumAssignment
knapsack               ortools.algorithms.python.knapsack_solver   KnapsackSolver
other top-level packages: bop, glop, init, packing, pdlp, scheduling, service, set_cover, util
```

Every import worked and no name is missing. Read the table as the package's map:

- **MathOpt** (`math_opt`) is OR-Tools' solver-independent modeling layer for LP and MILP: you write
  a model of variables, linear constraints and an objective once, and hand it to any of several
  solvers (lesson 1.1.3 met it; the next two modules, *MathOpt core* and *MathOpt advanced*, teach it).
- **CP-SAT** (`sat`) is Google's constraint-programming solver over integers (the module *CP-SAT core*, from lesson 4.4.1). It has its
  own model class, and it is also one of the solvers MathOpt can hand a model to.
- **The linear solver wrapper** (`linear_solver`, imported as `pywraplp`) is OR-Tools' older API for
  LP and MILP models, with the same idea as MathOpt (one model, a choice of solvers) and a different
  syntax. Existing code often uses it, and so do the OR-Tools guide pages on LP and MIP; lessons 4.7.1 and
  4.7.2 teach you to read it and move it to MathOpt.
- **Routing** lives in `constraint_solver`, in the same `pywrapcp` module as OR-Tools' original
  constraint solver (which this course does not use). In 9.15 there is no `ortools.routing` Python
  package; the OR-Tools 9.15 routing samples import from `ortools.constraint_solver` too.
- **Graph** (`graph`) holds the network solvers: maximum flow, minimum-cost flow and the assignment
  solver. **Knapsack** sits on its own, in `algorithms`.

The "other" line is the rest of the wheel. Some of it is plumbing the families use (`init`, `util`,
`service`, and the parameter definitions in `glop`, `bop`, `pdlp`); some is outside this course
(`set_cover`, `packing`, `scheduling`'s file readers). You will not import them in section 4.

A **wrapper**, in all of this, is a Python layer over C++ code: every solver here is written in C++
and compiled into the wheel, and the Python modules call into it. That is why a solver can print
straight to your terminal past Python's `print` (lesson 4.2.1, later in this section, meets HiGHS
lines printed that way), and why lesson 4.1.2 finds some errors only in a log.

## MathOpt, CP-SAT and the Linear Solver Wrapper Each Take a General Model

Three of the families take a **general model**: any variables, any linear rows, an objective. Job 1
fits all three. Here it is in each, from one program that builds the same dicts of values `value`,
costs `cost` and the `budget` from GridCap tiny first. MathOpt:

```python
def with_mathopt() -> list[str]:
    model = mathopt.Model(name="budget_pick")
    x = {i: model.add_binary_variable(name=f"x_{i}") for i in ids}
    model.add_linear_constraint(sum(cost[i] * x[i] for i in ids) <= budget, name="budget")
    model.maximize(sum(value[i] * x[i] for i in ids))
    with muted():
        result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return [i for i in ids if result.variable_values(x[i]) > 0.5]
```

`muted()` is the course's small helper (`quiet.py`) that keeps what the C++ solver writes to the
terminal off the output. CP-SAT, in its own API:

```python
def with_cp_sat() -> list[str]:
    model = cp_model.CpModel()
    x = {i: model.new_bool_var(f"x_{i}") for i in ids}
    model.add(sum(cost[i] * x[i] for i in ids) <= budget)
    model.maximize(sum(value[i] * x[i] for i in ids))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return [i for i in ids if solver.value(x[i])]
```

And the linear solver wrapper, with SCIP as its solver:

```python
def with_pywraplp() -> list[str]:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    x = {i: solver.BoolVar(f"x_{i}") for i in ids}
    solver.Add(sum(cost[i] * x[i] for i in ids) <= budget, "budget")
    solver.Maximize(sum(value[i] * x[i] for i in ids))
    solver.Solve()
    return [i for i in ids if x[i].solution_value() > 0.5]
```

The three functions are the same five steps (a model, binary variables, the budget row, the
objective, a solve) with three spellings. Where they differ is the point:

| | MathOpt | CP-SAT | linear solver wrapper |
| --- | --- | --- | --- |
| the model | `mathopt.Model` | `cp_model.CpModel` | the solver object itself |
| the solver is chosen | at `solve`, as `SolverType.HIGHS` | always CP-SAT | at creation, as `CreateSolver("SCIP")` |
| variables | continuous, integer, binary | integer and Boolean only | continuous, integer, binary |
| reading a value | `result.variable_values(x)` | `solver.value(x)` | `x.solution_value()` |

The second row is the one that shapes code. MathOpt keeps the model free of any solver, so switching
solver is one argument (lesson 4.2.3). The wrapper builds the model *inside* a solver object, so
switching means recreating it. CP-SAT is one solver, with an API made for it. The third row is the
other split: CP-SAT has no continuous variable at all (lesson 4.4.1), so a model with amounts that
can be fractional belongs in MathOpt or the wrapper.

Two things the short CP-SAT function above skips, which any real use needs. First, `solver.solve`
returns a **status**, the solver's verdict, and a program reads it before it reads a plan:
`cp_model.OPTIMAL` means the plan is proven best, `cp_model.FEASIBLE` that a limit stopped the
search with a plan that is not proven best, and the others (`INFEASIBLE`, `MODEL_INVALID`,
`UNKNOWN`) leave no plan to read. Second, CP-SAT's rows take whole-number coefficients only (lesson
4.1.2 shows a row with 0.37 in it refused), but its objective may have decimals. The program solves
the budget pick once more, with NPV in $M to two decimals, and checks the status first:

```python
model.maximize(sum(round(value[i] / 1000, 2) * x[i] for i in ids))      # NPV in $M, two decimals
solver = cp_model.CpSolver()
status = solver.solve(model)
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):             # a plan to read; OPTIMAL also proves it best
    print(f"CP-SAT status {solver.status_name(status)}, objective {solver.objective_value:.2f} $M,",
          " ".join(i for i in ids if solver.value(x[i])))
print("CP-SAT statuses:", ", ".join(cp_model.CpSolverStatus.__members__))
```

```text
CP-SAT status OPTIMAL, objective 4.88 $M, P001 P004 P005 P006
CP-SAT statuses: UNKNOWN, MODEL_INVALID, FEASIBLE, INFEASIBLE, OPTIMAL
```

The decimal objective was accepted and gave the same four projects. Lesson 4.4.1 teaches the
statuses in full, and lesson 4.4.3 how CP-SAT handles an objective with decimals.

<!-- practice 1 -->

## The Special-Purpose Solvers Take One Problem Shape, and No Model at All

The rest of the package does not take models. A **special-purpose solver** is an algorithm for one
problem shape: you hand it the data of that shape (values and weights, a cost matrix, a network) and
it hands back the answer. There are no variables and no constraints to write, and nothing else can be
added. Job 1 is a knapsack, so the knapsack solver takes it as three lists, adapted from the OR-Tools
example `knapsack.py`:

```python
def with_knapsack_solver() -> list[str]:
    solver = knapsack_solver.KnapsackSolver(
        knapsack_solver.SolverType.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, "budget_pick")
    solver.init([value[i] for i in ids], [[cost[i] for i in ids]], [budget])
    solver.solve()
    return [i for n, i in enumerate(ids) if solver.best_solution_contains(n)]
```

`init` takes the values, a list of weight rows (one row per capacity; here one, the budget) and the
capacities. The program runs all four functions:

```python
answers = {"MathOpt (HiGHS)": with_mathopt(), "CP-SAT": with_cp_sat(),
           "pywraplp (SCIP)": with_pywraplp(), "KnapsackSolver": with_knapsack_solver()}
print(f"GridCap tiny: {len(ids)} projects, budget {budget:,} $k")
for api, chosen in answers.items():
    total = sum(value[i] for i in chosen)
    spent = sum(cost[i] for i in chosen)
    print(f"{api:<16} NPV {total:>5,}  spend {spent:,}  {' '.join(chosen)}")
print("all four choose the same projects:", len({tuple(c) for c in answers.values()}) == 1)
```

```text
GridCap tiny: 8 projects, budget 7,390 $k
MathOpt (HiGHS)  NPV 4,876  spend 7,370  P001 P004 P005 P006
CP-SAT           NPV 4,876  spend 7,370  P001 P004 P005 P006
pywraplp (SCIP)  NPV 4,876  spend 7,370  P001 P004 P005 P006
KnapsackSolver   NPV 4,876  spend 7,370  P001 P004 P005 P006
all four choose the same projects: True
```

Four APIs, one answer: fund P001, P004, P005 and P006 for $4,876k of NPV, spending $7,370k of the
$7,390k. The knapsack solver needed the least code, and it is the least flexible. It takes more
capacity rows (one weight row per capacity), but nothing else: GridCap's real selection also has
must-do projects, "at most one of these alternatives" and "a child only with its parent" (lesson
4.2.1), and `init` has no argument for any of them. The moment a rule is not a capacity, the general
model is the tool.

Job 2 is an assignment problem, and the graph package has a solver for exactly that shape,
`SimpleLinearSumAssignment`, adapted here from the OR-Tools example
`assignment_linear_sum_assignment.py`. Its input is one arc per (crew, site) pair with a cost:

```python
def with_assignment_solver() -> tuple[int, list[int]]:
    solver = linear_sum_assignment.SimpleLinearSumAssignment()
    for k in range(len(crews)):
        for s in range(len(sites)):
            solver.add_arc_with_cost(k, s, hours[k][s])
    status = solver.solve()
    assert status == solver.OPTIMAL, status
    return solver.optimal_cost(), [solver.right_mate(k) for k in range(len(crews))]
```

`right_mate(k)` is the site paired with crew `k`. The same program also writes Job 2 as the general
model of the formulation, in CP-SAT, with one `add_exactly_one` per crew and per site:

```python
def with_cp_sat() -> tuple[int, list[int]]:
    model = cp_model.CpModel()
    y = {(k, s): model.new_bool_var(f"y_{k}_{s}") for k in range(len(crews)) for s in range(len(sites))}
    for k in range(len(crews)):
        model.add_exactly_one(y[k, s] for s in range(len(sites)))        # each crew gets one site
    for s in range(len(sites)):
        model.add_exactly_one(y[k, s] for k in range(len(crews)))        # each site gets one crew
    model.minimize(sum(hours[k][s] * y[k, s] for (k, s) in y))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return int(solver.objective_value), [next(s for s in range(len(sites)) if solver.value(y[k, s]))
                                         for k in range(len(crews))]
```

```text
assignment solver 15 hours  Ridge->S2, Valley->S1, Coast->S3, Plains->S4
CP-SAT            15 hours  Ridge->S2, Valley->S1, Coast->S3, Plains->S4
```

Both find the 15-hour plan. It is not the plan of sending each crew to its own nearest site: the
Plains crew's nearest is S1 (5 hours), which the Valley crew needs more (2 hours), so Plains goes to
S4 (6 hours). Finding that is the whole job of an assignment algorithm.

`with_assignment_solver` checks `solve()`'s return value before it reads a cost. That value is a
status, and the assignment solver has three. When no pairing exists, it says so in the status and
raises nothing:

```python
print("statuses:", ", ".join(linear_sum_assignment.SimpleLinearSumAssignment.Status.__members__))
stuck = linear_sum_assignment.SimpleLinearSumAssignment()
stuck.add_arc_with_cost(0, 0, 4)                 # two crews, and both cleared only for site 0
stuck.add_arc_with_cost(1, 0, 2)
status = stuck.solve()
print("two crews, one usable site:", status.name, "| status == stuck.OPTIMAL:", status == stuck.OPTIMAL)
```

```text
statuses: OPTIMAL, INFEASIBLE, POSSIBLE_OVERFLOW
two crews, one usable site: INFEASIBLE | status == stuck.OPTIMAL: False
```

Compare the status with the solver's own `OPTIMAL` (`solver.OPTIMAL`), and read `optimal_cost()` and
`right_mate` only when they are equal. `POSSIBLE_OVERFLOW` means the costs are too large for the
solver's whole-number arithmetic.

The other two graph solvers take networks: `SimpleMaxFlow` (the most that can move from a source to
a sink through arcs of limited capacity) and `SimpleMinCostFlow` (move given supplies to given
demands at least cost). Lessons 4.7.3 and 4.7.4 teach all three, plus the knapsack solver, and checks each
against the MIP it replaces. Two facts about them come up in lesson 4.1.2: they take whole numbers
only (a fraction raises a `TypeError`), and the flow and assignment solvers report an impossible
problem through a status returned by `solve`, not an exception.

<!-- practice 2 -->

## Routing Is Its Own Library, Built Around Vehicles, Stops and Callbacks

Job 3 goes to the routing library, a solver made for vehicle routes: one or many vehicles, a depot,
stops, and the rules real routes carry (vehicle capacities, time windows, stops that may be dropped
at a price; the OR-Tools routing guide lists these as variants of the vehicle routing problem). The
program is adapted from the OR-Tools example `tsp_cities.py`, with five invented substations on a
grid of km:

```python
manager = pywrapcp.RoutingIndexManager(len(names), 1, 0)      # stops, vehicles, depot
routing = pywrapcp.RoutingModel(manager)


def distance(from_index: int, to_index: int) -> int:
    return km[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]


routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(distance))
params = pywrapcp.DefaultRoutingSearchParameters()
params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(params)
```

```text
status: ROUTING_SUCCESS
possible statuses: ROUTING_NOT_SOLVED, ROUTING_SUCCESS, ROUTING_PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED, ROUTING_FAIL, ROUTING_FAIL_TIMEOUT, ROUTING_INVALID, ROUTING_INFEASIBLE, ROUTING_OPTIMAL
route: Depot -> S5 -> S1 -> S2 -> S3 -> S4 -> Depot
length: 40 km
```

Three things in this code exist nowhere else in OR-Tools:

1. **An index manager.** `RoutingIndexManager(stops, vehicles, depot)` translates between your stop
   numbers ("nodes") and the solver's internal indices, which are different because each vehicle has
   its own start and end. Every callback converts with `IndexToNode`.
2. **Costs as callbacks.** You do not give the solver a matrix; you register a Python function
   (`RegisterTransitCallback`) that it calls for the cost of any arc, and tell it that function is
   the cost of every vehicle.
3. **A search, steered by parameters.** `PATH_CHEAPEST_ARC` is the rule for the first route: start
   at the depot and keep extending the route by the cheapest next leg. How the search goes on from
   that first route is set by more parameters (lesson 4.8.5).

The status is `ROUTING_SUCCESS`, not `ROUTING_OPTIMAL`. Both names are in the library's status
list, printed above, and `ROUTING_SUCCESS` means it found a route, not that it proved none is
shorter. The OR-Tools routing guide says the same in plain words: the library sometimes returns routes that are good
rather than optimal. That is the trade the routing library makes, and it is why a planner who needs
proven optima on a small instance still writes a MILP. The routing lessons at the end of this
section, from lesson 4.8.1 on, teach the library: dimensions, capacities, time windows, droppable visits and the
search settings.

## Summary

- **OR-Tools is one pip package with separate solver families**, each in its own module:
  `math_opt`, `sat`, `linear_solver` (`pywraplp`), `constraint_solver` (`pywrapcp`, routing),
  `graph` and `algorithms` (knapsack).
- **MathOpt, CP-SAT and the linear solver wrapper take a general model.** They spell the same five
  steps differently; MathOpt names the solver at `solve`, the wrapper at creation, and CP-SAT is its
  own solver with integers only.
- **The special-purpose solvers take one problem shape and no model.** The knapsack and assignment
  solvers matched the general models' answers here, with less code and no room for a single extra
  rule.
- **Routing is its own library**: an index manager, cost callbacks and a search, which returns good
  routes (`ROUTING_SUCCESS`) without proving them optimal.

## Reference

| Family | Import | Takes | Taught in section 4 by |
| --- | --- | --- | --- |
| MathOpt | `from ortools.math_opt.python import mathopt` | LP and MILP models; solver chosen at `solve` | the modules *MathOpt core* and *MathOpt advanced* |
| CP-SAT | `from ortools.sat.python import cp_model` | integer and Boolean models, logic, intervals | the modules *CP-SAT core*, *CP-SAT scheduling*, *CP-SAT tuning and diagnostics* |
| linear solver wrapper | `from ortools.linear_solver import pywraplp` | LP and MILP models; solver chosen at creation | lessons 4.7.1 and 4.7.2 |
| graph | `from ortools.graph.python import max_flow, min_cost_flow, linear_sum_assignment` | networks; cost matrices | lessons 4.7.3 and 4.7.4 |
| knapsack | `from ortools.algorithms.python import knapsack_solver` | values, weight rows, capacities | lesson 4.7.4 |
| routing | `from ortools.constraint_solver import pywrapcp, routing_enums_pb2` | stops, vehicles, cost callbacks | the module *OR-Tools routing* |

| Problem | Name used in this course |
| --- | --- |
| pick items under capacities | knapsack |
| pair two groups one to one at least cost | assignment |
| most that fits through a capacitated network | maximum flow |
| supplies to demands at least cost | minimum-cost flow |
| one vehicle, every stop once, shortest round trip | traveling salesperson (TSP) |
| many vehicles, stops shared among them | vehicle routing (VRP) |

**Further reading:** [About OR-Tools](https://developers.google.com/optimization/introduction) (the
problem types and the families: constraint programming, linear and mixed-integer programming, vehicle
routing, graph algorithms); [OR-Tools overview](https://developers.google.com/optimization) (the
solvers OR-Tools can call, open source and commercial); [Get Started with OR-Tools for
Python](https://developers.google.com/optimization/introduction/python) (identify the problem type,
then choose a solver; a first `pywraplp` program); [MathOpt](https://developers.google.com/optimization/math_opt)
(modeling separated from solving, and the problem types it takes); [CP-SAT
Solver](https://developers.google.com/optimization/cp/cp_solver) (CP-SAT works over the integers);
[The Knapsack Problem](https://developers.google.com/optimization/pack/knapsack) and the sample
[`knapsack.py`](https://github.com/google/or-tools/blob/v9.15/ortools/algorithms/samples/knapsack.py);
[Solving an Assignment Problem with the Linear Sum Assignment Solver](https://developers.google.com/optimization/assignment/linear_assignment)
and the sample [`assignment_linear_sum_assignment.py`](https://github.com/google/or-tools/blob/v9.15/ortools/graph/samples/assignment_linear_sum_assignment.py)
(a specialized solver that can be faster than the MIP or CP-SAT solvers, integer costs only);
[Network Flows](https://developers.google.com/optimization/flow) and
[Maximum Flows](https://developers.google.com/optimization/flow/maxflow) (the graph package's flow
solvers); [Vehicle Routing](https://developers.google.com/optimization/routing) (the routing variants,
and routes that are good but not always optimal); [Traveling Salesperson
Problem](https://developers.google.com/optimization/routing/tsp) and the sample
[`tsp_cities.py`](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/tsp_cities.py)
(the index manager, the transit callback and `PATH_CHEAPEST_ARC`).

## Challenges

1. Add the rule "at most one of P006 and P007" to Job 1 in all four APIs. Which of the four cannot
   take it, and what is the smallest change in each of the others?
2. In `crew_sites.py`, give the Plains crew a 1-hour trip to S4. Predict the new plan before running.
3. In `inspection_route.py`, change the first-solution strategy to `GLOBAL_CHEAPEST_ARC`. Does the
   route length change? Does the status?

## Design Note: The Family Is Chosen by the Problem's Shape, Not by Habit

All four APIs answered Job 1 the same way, and that is the usual case for small problems: the choice
of family rarely changes the answer, but it decides what you can add later. A knapsack solver is a
dead end the day a must-do rule arrives; a general model is not. A routing library gives up proofs of
optimality to handle routes that a MILP could not solve in time at all. Lesson 4.1.3 turns these
trade-offs into a procedure.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**package_map.py.** Imports each family's module and lists the rest of the wheel (*OR-Tools Is One
pip Package*). *Try:* Add `("graph: shortest paths", "ortools.graph.python.shortest_paths", [])`.
Predict whether it imports in 9.15.

- Program: [package_map.py](src/package_map.py)

**budget_pick.py.** Job 1 in MathOpt, CP-SAT, the linear solver wrapper and the knapsack solver
(*MathOpt, CP-SAT and the Linear Solver Wrapper*, *The Special-Purpose Solvers*). *Try:* Lower the
budget by 1,000. Predict whether the four still agree.

- Program: [budget_pick.py](src/budget_pick.py)

**crew_sites.py.** Job 2 with the assignment solver and with CP-SAT (*The Special-Purpose Solvers*).
*Try:* Add a fifth crew with a row of hours and no fifth site. Predict what each solver does.

- Program: [crew_sites.py](src/crew_sites.py)

**inspection_route.py.** Job 3 with the routing library (*Routing Is Its Own Library*). *Try:* Move
S5 Mesa to (9, 0). Predict where it lands in the route.

- Program: [inspection_route.py](src/inspection_route.py)

**quiet.py.** The helper that keeps C++ solvers' terminal output off the printed results.

- Library: [quiet.py](src/quiet.py)
