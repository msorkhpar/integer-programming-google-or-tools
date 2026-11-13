# 4.8.1 The Routing Model: Index Manager, Transit Callbacks and the TSP

GridCap's asset-health model flags eight substation transformers in the Valley region as urgent:
each has five years or less of predicted remaining life (RUL), and each needs an on-site
inspection with an oil sample. One crew leaves the Valley yard in the morning, drives to all
eight sites and comes back. In what order should it drive them to spend the least time on the road?

That question is the **traveling salesperson problem (TSP)**: one vehicle, a set of places, visit
each exactly once and return to the start, at the least total cost. Eight sites can be driven in
8! = 40,320 orders, so you could try them all. With 18 sites there are about 6.4 × 10¹⁵ orders, so
you cannot. Add more crews and you have a **vehicle routing problem (VRP)**: several vehicles
share the visits, and each visit goes to exactly one of them. The OR-Tools **routing library**
solves both, along with the variants the rest of this module adds: capacities, time windows,
optional visits, pickup and delivery.

This lesson builds the smallest routing model, the TSP, with the four pieces every routing model
has: an index manager, a routing model, a transit callback that prices each arc, and search
parameters. It starts with the OR-Tools TSP guide's own example and then moves to the Valley crew.

GridCap is fictional, and it has no map. `valley.py` places the Valley yard and substations on an
invented 30 × 30 km map, from a fixed seed, and turns straight-line distance into drive minutes at
40 km/h. So every drive time in this module is made up, and the same on every run.

## A Routing Model Chooses a Successor for Every Stop

A MIP (lessons 3.1.1 to 3.4.3) is a set of numeric variables, linear rows and a linear objective,
solved by branch and bound. The routing library works differently, and you should be able to say
how in an interview.

It gives every stop one decision variable, its **successor**: $`\text{next}_i`$, the stop the
vehicle drives to after leaving $`i`$. A route is what you get by starting at the depot (the
place where vehicles start and end, here the yard) and following the successors until you come
back. The cost of the route is the sum of the costs of the **arcs** it drives, an arc being one
ordered pair (from, to). The library's constraints say that the successors form complete routes:
no two stops share a successor, and every chain of successors starts at a vehicle's start and ends
at that vehicle's end, with no closed loop of stops that never touches the depot (a **subtour**).

How does it search? The routing library is built on OR-Tools' original constraint-programming
solver (the `pywrapcp` module, "cp" for constraint programming). It first builds one complete set
of routes with a fast rule, the **first-solution strategy** (here `PATH_CHEAPEST_ARC`: from the
current stop, drive to the cheapest unvisited one). Then it runs **local search**: it tries small
changes to the routes (move a stop, swap two stops, reverse a segment) and keeps any change that
lowers the cost, until no change helps. Lesson 4.8.5 covers both in depth.

Two consequences matter in practice:

- The answer is a good set of routes, not one with a proof of optimality. A MIP solver reports a
  bound and a gap (lesson 3.4.1); the routing library reports neither.
- The costs must be **integers**. Every cost and every quantity the model adds up is a 64-bit
  integer, so a cost in fractional minutes must be scaled (third section below).

For contrast, here is how a MIP would state the same TSP. Give each ordered pair one binary
$`x_{ij}`$, equal to 1 if the vehicle drives from $`i`$ straight to $`j`$:

```math
\begin{aligned}
\min \; & \sum_{i \in N} \sum_{j \in N,\, j \ne i} c_{ij}\, x_{ij} \\
\text{s.t.} \; & \sum_{j \ne i} x_{ij} = 1 && \forall i \in N && \text{(leave each stop once)} \\
& \sum_{i \ne j} x_{ij} = 1 && \forall j \in N && \text{(enter each stop once)} \\
& \sum_{i \in S} \sum_{j \in S,\, j \ne i} x_{ij} \le |S| - 1 && \forall S \subset N,\ 2 \le |S| \le |N| - 1 && \text{(no subtour inside } S\text{)} \\
& x_{ij} \in \{0, 1\} && \forall i \ne j
\end{aligned}
```

The first two rows alone allow two separate small loops; the subtour rows forbid them, and there
is one for every subset $`S`$ of stops, so their number grows as $`2^{|N|}`$. A MIP solver adds
them only as they are needed. The routing library never writes them: its successor variables and
path constraints keep each route connected by construction. Both are valid models of the same
problem; they search differently.

## The Index Manager Translates Between Your Nodes and the Solver's Indices

Your data is indexed by **node**: row and column $`i`$ of the distance matrix is place $`i`$, with
the depot usually node 0. The solver works in its own **indices**, because each vehicle needs a
separate start and end: with two vehicles, the depot is the start of vehicle 0, the start of
vehicle 1, the end of vehicle 0 and the end of vehicle 1, four different indices for one node.
`RoutingIndexManager` creates that numbering and converts in both directions. Its three arguments
are the number of nodes, the number of vehicles and the depot node:

```python
def index_table(num_nodes: int, num_vehicles: int, depot: int) -> None:
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    for index in range(routing.Size() + num_vehicles):
        role = (f"start of vehicle {routing.VehicleIndex(index)}" if routing.IsStart(index)
                else f"end of vehicle {routing.VehicleIndex(index)}" if routing.IsEnd(index) else "a visit")
        print(f"  index {index:2}  node {manager.IndexToNode(index)}  {role}")
```

`routing.Size()` counts the indices that have a successor variable (the visits and the starts);
the ends come after them, one per vehicle. For five nodes:

```text
5 nodes, 1 vehicle(s), depot 0: routing.Size() = 5, 6 indices in all
  index  0  node 0  start of vehicle 0
  index  1  node 1  a visit
  index  2  node 2  a visit
  index  3  node 3  a visit
  index  4  node 4  a visit
  index  5  node 0  end of vehicle 0
5 nodes, 2 vehicle(s), depot 0: routing.Size() = 6, 8 indices in all
  index  0  node 0  start of vehicle 0
  index  1  node 1  a visit
  index  2  node 2  a visit
  index  3  node 3  a visit
  index  4  node 4  a visit
  index  5  node 0  start of vehicle 1
  index  6  node 0  end of vehicle 0
  index  7  node 0  end of vehicle 1
5 nodes, 1 vehicle(s), depot 3: routing.Size() = 5, 6 indices in all
  index  0  node 0  a visit
  index  1  node 1  a visit
  index  2  node 2  a visit
  index  3  node 3  start of vehicle 0
  index  4  node 4  a visit
  index  5  node 3  end of vehicle 0
```

With one vehicle, index and node agree everywhere except the end (index 5 is node 0). With two
vehicles, indices 5, 6 and 7 are all node 0. Index 5 or 6 or 7 used as a row of a 5-row matrix is
off the end. So the rule is: **the solver hands you indices, your data wants nodes, and the
manager converts**. `manager.IndexToNode(index)` goes one way, `manager.NodeToIndex(node)` the
other (you need it to attach a rule to a place, from lesson 4.8.3 on).

The manager can also give each vehicle its own start and end node:
`RoutingIndexManager(num_nodes, num_vehicles, starts, ends)`, with one list entry per vehicle. The
OR-Tools "common routing tasks" guide shows it; this module's crews all start and end at one yard.

## A Transit Callback Returns the Integer Cost of One Arc

The model learns what an arc costs through a **transit callback**: a Python function the solver
calls with two indices (from, to) and that returns the cost of driving that arc. You register it
with the model, which gives back an integer handle, and then tell the model to use it as the arc
cost of every vehicle. Here is the OR-Tools TSP guide's example, which plans one vehicle through 13
cities with distances in miles:

```python
# 1. The index manager: number of nodes, number of vehicles, the depot node.
manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
# 2. The routing model, built on the manager.
routing = pywrapcp.RoutingModel(manager)
# 3. The transit callback: the solver passes two routing indices; turn them into nodes, look up the arc.
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]
transit_callback_index = routing.RegisterTransitCallback(distance_callback)
# 4. The arc cost: every vehicle pays the callback's value for every arc it drives.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
```

Three things to notice:

- The callback converts both indices to nodes before it reads the matrix, for the reason the
  previous section showed.
- `RegisterTransitCallback` returns an integer, the callback's handle. Every later call that needs
  the callback (the arc cost here, dimensions in lesson 4.8.2) takes that handle, not the
  function.
- `SetArcCostEvaluatorOfAllVehicles` makes the callback the objective: the model minimizes the sum
  of the callback's values over every arc driven. A different cost per vehicle is possible with
  `SetArcCostEvaluatorOfVehicle(handle, vehicle)`.

The callback must return an integer. GridCap's drive times start as fractional minutes
(1.5 minutes per km of straight-line distance). `integer_costs.py` passes those floats straight
through, then rounds them two ways:

```python
try:
    solve_tour(exact_minutes)
except Exception as error:   # the solver cannot use a float arc cost
    print(f"float callback: {type(error).__name__}")
for scale, unit in ((1, "whole minutes"), (10, "tenths of a minute")):
    objective, tour = solve_tour(lambda a, b: round(scale * exact_minutes(a, b)))
```

```text
float callback: SystemError
cost in whole minutes: objective 106 = 106.0 min, tour [0, 1, 5, 6, 2, 3, 7, 8, 4, 0], exact length 105.99 min
cost in tenths of a minute: objective 1060 = 106.0 min, tour [0, 1, 5, 6, 2, 3, 7, 4, 8, 0], exact length 105.85 min
```

A float return does not get rounded for you: the solve fails, with an error that does not say
why. Rounding to whole minutes works, but it changes the costs the solver compares: the
whole-minute tour is 105.99 exact minutes long, and the tenths-of-a-minute model finds a different
tour (it drives 7, 4, 8 instead of 7, 8, 4) that is truly shorter, 105.85 minutes. Both report 106
minutes once divided back. The rule: **multiply by a scale that keeps the precision you care
about, round, and divide the objective by the same scale when you report it.** The TSP guide's
circuit-board example truncates with `int()` instead, and says rounding can change the answer in
other cases; this is one of them.

<!-- practice 1 -->

## Solve, Then Walk Each Route From Start to End

Two more steps finish the model. The **search parameters** say how to search; the defaults come
from `DefaultRoutingSearchParameters()`, and the guides set the first-solution strategy explicitly.
`SolveWithParameters` runs the search and returns an **assignment** (a value for every variable),
or `None` if it found no routes. Here is the Valley crew's tour of its eight urgent sites, with
the yard as node 0:

```python
manager = pywrapcp.RoutingIndexManager(len(places), 1, YARD)
routing = pywrapcp.RoutingModel(manager)
def drive(from_index, to_index):
    """Minutes from one stop to the next; the solver speaks in indices, the matrix in nodes."""
    return minutes[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
drive_index = routing.RegisterTransitCallback(drive)
routing.SetArcCostEvaluatorOfAllVehicles(drive_index)
parameters = pywrapcp.DefaultRoutingSearchParameters()
parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
solution = routing.SolveWithParameters(parameters)
```

The assignment does not hold a list of stops. It holds a successor for each index, and you rebuild
the route by walking it: start at `routing.Start(vehicle)`, read the successor with
`solution.Value(routing.NextVar(index))`, and stop when `routing.IsEnd(index)` is true. The end is
a separate index, so you add its node after the loop:

```python
def route_of(vehicle: int) -> list[int]:
    """The nodes vehicle drives through, from its start to its end, read off the NextVar values."""
    index, nodes = routing.Start(vehicle), []
    while not routing.IsEnd(index):
        nodes.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    return nodes + [manager.IndexToNode(index)]
```

The program also tries all 40,320 orders by brute force, a check the routing library cannot give:

```text
route: YARD -> A087 -> A230 -> A308 -> A106 -> A136 -> A348 -> A378 -> A157 -> YARD
nodes: [0, 1, 5, 6, 2, 3, 7, 8, 4, 0]
drive minutes (objective): 106
drive minutes, arc by arc: 10 + 4 + 7 + 8 + 24 + 8 + 20 + 1 + 24
brute force over every order: best 106 minutes
```

`solution.ObjectiveValue()` is the sum of the arc costs, and the arc-by-arc line adds up to the
same 106. On this small instance the route is as short as any order can be. On 18 sites no brute
force is possible, and nothing in the solution tells you how far from the best it is; lesson 4.8.5
returns to that.

The OR-Tools TSP guide's own example runs the same steps, and in this module's runner it prints
the route and the 7,293-mile total the guide shows:

```text
Objective: 7293 miles
Route for vehicle 0: 0 -> 7 -> 2 -> 3 -> 4 -> 12 -> 6 -> 8 -> 1 -> 11 -> 10 -> 5 -> 9 -> 0
Route distance: 7293 miles
```

The walk adds `routing.GetArcCostForVehicle(previous_index, index, 0)` for each arc it drives,
which is how the guide's printer gets "Route distance" without reading the matrix.

<!-- practice 2 -->

## The Model

What the routing model in `valley_tsp.py` encodes. It is a **vehicle routing model**, not an LP or
MIP: the variables are successors, and the solver is a constraint-programming search with
heuristics, so no row below is sent to an LP solver.

**Sets.** $`N = \{0, 1, \dots, n\}`$ the nodes, node 0 the yard and nodes 1 to $`n`$ the sites;
$`V`$ the vehicles (one crew here); $`I`$ the solver's indices: one per site, plus a start
$`s_v`$ and an end $`e_v`$ per vehicle $`v \in V`$; $`\text{node}(i)`$ the node of index $`i`$
(`manager.IndexToNode`).

**Parameters.** $`c_{ab} \in \mathbb{Z}_{\ge 0}`$, the drive minutes from node $`a`$ to node
$`b`$ (rounded, fictional); the transit callback returns $`c_{\text{node}(i),\, \text{node}(j)}`$
for indices $`i, j`$.

**Variables.** $`\text{next}_i \in I \setminus \{s_v : v \in V\}`$ for every index $`i`$ that is
not an end: the index the vehicle drives to after $`i`$ (`routing.NextVar(i)`).
$`\text{vehicle}_i \in V`$ for every index: the vehicle that visits $`i`$
(`routing.VehicleVar(i)`, used from lesson 4.8.4 on).

**Objective.**

```math
\min \; \sum_{i \in I \setminus \{e_v\}} c_{\text{node}(i),\, \text{node}(\text{next}_i)}
```

**Constraints.**

```math
\begin{aligned}
& \text{next}_i \ne \text{next}_j && \forall i \ne j && \text{(one predecessor each)} \\
& \text{the chain } s_v, \text{next}_{s_v}, \text{next}_{\text{next}_{s_v}}, \dots \text{ ends at } e_v && \forall v \in V && \text{(routes, no subtours)} \\
& \text{vehicle}_{\text{next}_i} = \text{vehicle}_i && \forall i && \text{(a route keeps its vehicle)} \\
& \text{every site index lies on some route} && && \text{(visit every site)}
\end{aligned}
```

| Label | Where it comes from in the code |
| --- | --- |
| objective | `SetArcCostEvaluatorOfAllVehicles(drive_index)` |
| one predecessor each, routes, a route keeps its vehicle | built into `RoutingModel`; you never write them |
| visit every site | the default; lesson 4.8.4 makes a visit optional |

## Summary

- **A routing model chooses a successor for every stop.** Its constraints keep the successors in
  complete routes from each vehicle's start to its end, with no subtours; the search builds a
  first solution and improves it by local search, with no optimality proof.
- **The index manager translates between your nodes and the solver's indices.** Each vehicle has
  its own start and end index, so convert every index with `IndexToNode` before you read your data.
- **A transit callback returns the integer cost of one arc.** Register it, pass its handle to
  `SetArcCostEvaluatorOfAllVehicles`, and scale fractional costs to integers yourself.
- **Solve, then walk each route from start to end.** Follow `NextVar` from `routing.Start(v)`
  until `routing.IsEnd`, and add the end's node after the loop.

## Reference

| Call | What it does |
| --- | --- |
| `pywrapcp.RoutingIndexManager(n, vehicles, depot)` | numbers the solver's indices; `(n, vehicles, starts, ends)` gives each vehicle its own start and end |
| `manager.IndexToNode(i)`, `manager.NodeToIndex(a)` | index to your node, node to index |
| `pywrapcp.RoutingModel(manager)` | the routing model |
| `routing.RegisterTransitCallback(f)` | registers `f(from_index, to_index)`; returns its handle |
| `routing.SetArcCostEvaluatorOfAllVehicles(handle)` | the objective: the sum of `f` over the arcs driven |
| `pywrapcp.DefaultRoutingSearchParameters()` | default search parameters; set `first_solution_strategy` |
| `routing.SolveWithParameters(params)` | an assignment, or `None` |
| `routing.Start(v)`, `routing.IsEnd(i)`, `routing.NextVar(i)` | walk a route: `solution.Value(routing.NextVar(i))` |
| `solution.ObjectiveValue()` | the total cost |
| `routing.GetArcCostForVehicle(i, j, v)` | the cost of one arc for vehicle `v` |

Imports, as the OR-Tools 9.15 guides write them and as this course's runner has them:
`from ortools.constraint_solver import pywrapcp, routing_enums_pb2`.

**Further reading:** [OR-Tools: Vehicle routing](https://developers.google.com/optimization/routing),
[Traveling Salesperson Problem](https://developers.google.com/optimization/routing/tsp),
[Common routing tasks](https://developers.google.com/optimization/routing/routing_tasks), and the
samples [simple_routing_program.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/simple_routing_program.py)
and [tsp_cities.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/tsp_cities.py).

## Challenges

1. Add a ninth urgent site to the Valley list by hand. How many orders would the brute force try,
   and how long would it take at the speed you measure for eight?
2. Make every arc into the yard free (cost 0). What problem does the model now solve, and where
   does the route end in practice?
3. The TSP MIP above has one subtour row per subset of stops. Count them for 8 sites and for 18.

## Design Note: Why Not a MIP for Routing?

A MIP can solve the eight-site TSP exactly, and for small instances that proof is worth having. The
routing library is built for what comes next: hundreds of stops, many vehicles, time windows,
capacities and optional visits. There a MIP needs the subtour rows above plus a big-M row for every
arc and time window: a row that holds the arrival times in order when the arc is used, and is
switched off by a large constant $`M`$ when it is not (lesson 6.2.1, later in the course, derives
such rows in depth). Its model grows quickly, and a good route
found fast is usually worth more than a proof found late. The trade is the gap: a MIP
tells you how far from optimal it might be, the routing library does not. When a planner asks
"is this the best route?", the honest answer from the routing library is "the best this search
found". Lesson 4.8.5 shows how to make that search repeatable.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**index_manager.py.** Prints the solver's indices next to the nodes for one and two vehicles and a
depot that is not node 0 (*The Index Manager Translates Between Your Nodes and the Solver's
Indices*). *Try:* Print the table for 4 nodes and 3 vehicles. Before you run it, predict
`routing.Size()` and the index of each vehicle's end.

- Program: [index_manager.py](src/index_manager.py)

**tsp_cities.py.** The OR-Tools TSP guide's example, adapted with attribution (*A Transit Callback
Returns the Integer Cost of One Arc*). *Try:* Change the depot to city 7. Predict whether the tour
length changes.

- Program: [tsp_cities.py](src/tsp_cities.py)

**integer_costs.py.** A float callback, then whole-minute and tenth-of-a-minute costs on the
Valley tour (*A Transit Callback Returns the Integer Cost of One Arc*). *Try:* Use a scale of 100.
Predict whether the tour changes again.

- Program: [integer_costs.py](src/integer_costs.py)

**valley_map.py.** The Valley sites, with their invented coordinates, and the drive-minute matrix
(*A Transit Callback Returns the Integer Cost of One Arc*). *Try:* Find the two sites closest to
each other in the matrix, and check that the tour drives between them directly.

- Program: [valley_map.py](src/valley_map.py)

**valley_tsp.py.** One crew's tour of the eight urgent sites, checked by brute force (*Solve, Then
Walk Each Route From Start to End*). *Try:* Set the first-solution strategy to
`GLOBAL_CHEAPEST_ARC`. Predict whether the objective changes.

- Program: [valley_tsp.py](src/valley_tsp.py)

**valley.py.** The Valley instance the module's programs import: the sites, their invented map
positions, the drive-minute matrix and a clock helper. It runs nothing itself.

- Library: [valley.py](src/valley.py)
