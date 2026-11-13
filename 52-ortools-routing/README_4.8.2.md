# 4.8.2 Vehicles, Capacities and Dimensions (CVRP)

Lesson 4.8.1 sent one crew to the eight urgent Valley sites. The full list has 18 substations: the
eight urgent ones and ten routine inspections. That is too much for one crew, so three crews share
the day, and two limits appear. Each inspection uses one to three oil-sample kits (older
transformers need more samples), and a crew truck carries 12. And the union agreement caps a crew
at 150 minutes behind the wheel. The planner wants each site assigned to a crew, an order for each
crew, and both limits kept.

Several vehicles that share the visits make a **vehicle routing problem (VRP)**; with a load limit
per vehicle it is a **capacitated VRP (CVRP)**. This lesson adds both, and the one idea the routing
library uses for every quantity that builds up along a route: the **dimension**. The drive times
are fictional, as in lesson 4.8.1.

## One Index Manager Serves the Whole Fleet

More vehicles change one argument: the second argument of `RoutingIndexManager` is the number of
vehicles, and the manager creates a start and an end index for each (lesson 4.8.1's index table
showed two vehicles). Nothing else changes: one transit callback and one arc cost cover every
vehicle, and the solver decides which vehicle visits each site.

Each vehicle's route is read the same way as the TSP's, starting from `routing.Start(vehicle)`.
A vehicle with nothing to do drives from its start straight to its end; `routing.IsVehicleUsed(
solution, vehicle)` is false for it, and the guides' printers skip it.

Fewer total kilometers is not always what a planner wants, though. The OR-Tools VRP guide sends
four vehicles to 16 locations and wants the longest of the four routes to be as short as possible,
so that no driver gets a far longer day than the others. It gets that with a dimension, the next
section's subject. Here is its result, from this module's adapted
copy:

```text
Objective: 177500
vehicle 0: 0 -> 9 -> 10 -> 2 -> 6 -> 5 -> 0  (1712 m)
vehicle 1: 0 -> 16 -> 14 -> 8 -> 0  (1484 m)
vehicle 2: 0 -> 7 -> 1 -> 4 -> 3 -> 0  (1552 m)
vehicle 3: 0 -> 13 -> 15 -> 11 -> 12 -> 0  (1552 m)
total 6300 m, longest 1712 m, 100 x 1712 + 6300 = 177500
```

The objective is not the distance: it is 100 times the longest route plus the total. Where the
100 comes from is the next section.

## A Dimension Accumulates a Quantity Along Each Route

A **dimension** is a quantity that builds up as a vehicle drives its route: distance driven, time
on the clock, load in the truck. For every index $`i`$ it has three variables:

- the **cumul** $`\text{cumul}_i`$, the quantity's value when the vehicle arrives at $`i`$
  (`dimension.CumulVar(i)`);
- the **transit** $`\text{transit}_i`$, what the arc from $`i`$ to its successor adds, given by a
  callback;
- the **slack** $`\text{slack}_i \ge 0`$, an extra amount the vehicle may add at $`i`$ (waiting
  time, in lesson 4.8.3).

They are tied by one rule, written in the docstring of `AddDimension`:

```math
\text{cumul}_{\text{next}_i} = \text{cumul}_i + \text{transit}_i + \text{slack}_i
```

`routing.AddDimension(callback_handle, slack_max, capacity, fix_start_cumul_to_zero, name)` creates
one. `slack_max` bounds each slack, `capacity` bounds every cumul ($`0 \le \text{cumul}_i \le
\text{capacity}`$), the flag fixes the cumul at each vehicle's start to 0, and `name` is how you
get it back with `routing.GetDimensionOrDie(name)`. In the VRP guide's code:

```python
# A dimension named "Distance": no slack, at most 3000 m per vehicle, every route starts at 0.
routing.AddDimension(transit_callback_index, 0, 3000, True, "Distance")
distance_dimension = routing.GetDimensionOrDie("Distance")
# Add 100 x (longest route - shortest start) to the objective, so the longest route dominates.
distance_dimension.SetGlobalSpanCostCoefficient(100)
```

The same callback that prices the arcs now feeds the dimension, so a vehicle's cumul at its end is
the distance it drove, and the capacity 3000 caps every route at 3000 m. A dimension is a
**constraint** by default; it changes the objective only if you ask.
`SetGlobalSpanCostCoefficient(100)` asks: it adds 100 times the **global span**, the largest cumul
at any vehicle's end minus the smallest cumul at any vehicle's start. Every start is 0 here, so the
span is the longest route, and the objective becomes 100 × longest + total, the 177,500 above.

On the Valley day the same two calls cap each crew at 150 driving minutes and, in a second run,
weigh the longest drive by 100:

```python
# Drive: cumulative minutes behind the wheel, at most MAX_DRIVE for each crew.
routing.AddDimension(drive_index, 0, MAX_DRIVE, True, "Drive")
routing.GetDimensionOrDie("Drive").SetGlobalSpanCostCoefficient(span_coefficient)
```

The program walks crew 0's route in the second run and prints each stop's cumul next to the
transit of the arc leaving it. Each cumul is the previous one plus the previous transit (the slack
is 0):

```text
crew 0, stop by stop:
  YARD  drive cumul   0  transit to next  20
  A091  drive cumul  20  transit to next   2
  A106  drive cumul  22  transit to next  23
  A348  drive cumul  45  transit to next  10
  A149  drive cumul  55  transit to next  15
  A378  drive cumul  70  transit to next   1
  A157  drive cumul  71  transit to next  24
  YARD  drive cumul  95  (route end)
```

Where the dimension changes the plan is the comparison of the two runs:

```text
total drive only (span coefficient 0):
objective 234
  crew 0: A281 -> A302 -> A106 -> A096 -> A064 -> A136 -> A348  drive 107 min, kits 12
  crew 1: A149 -> A157 -> A378 -> A183 -> A133 -> A344  drive 75 min, kits 9
  crew 2: A305 -> A308 -> A091 -> A230 -> A087  drive 52 min, kits 12
longest drive weighted 100 (span coefficient 100):
objective 9756
  crew 0: A091 -> A106 -> A348 -> A149 -> A378 -> A157  drive 95 min, kits 12
  crew 1: A096 -> A064 -> A136 -> A183 -> A133 -> A344  drive 95 min, kits 9
  crew 2: A305 -> A281 -> A302 -> A308 -> A230 -> A087  drive 66 min, kits 12
```

With only the total in the objective, crew 0 drives 107 minutes and crew 2 drives 52. With the
span weighted, the longest drive falls to 95 minutes and the total rises from 234 to 95 + 95 + 66
= 256 minutes; the objective is 100 × 95 + 256 = 9,756. Which plan is better is a business
question: fewer kilometers, or a fairer day. The coefficient is how you answer it.

Read the cumul at the route's **end** index to get the route's total: `CumulVar(index)` after the
walk loop, where `index` is the end. That is how both printers get "drive 95 min".

<!-- practice 1 -->

## A Capacity Is a Dimension Whose Transit Is the Demand

A truck's load is a dimension too. Its transit at a stop is the stop's **demand** (here, the kits
the inspection uses), whatever stop comes next, so the callback takes one index, not two. The
guide calls it a **unary** callback and registers it with `RegisterUnaryTransitCallback`. The
capacity can differ by vehicle, so the guide uses `AddDimensionWithVehicleCapacity`, which takes a
list with one capacity per vehicle:

```python
def demand_callback(from_index):
    """A unary callback: the load picked up at one node, whatever comes next."""
    return demands[manager.IndexToNode(from_index)]
demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,                    # null capacity slack
    vehicle_capacities,   # one maximum load per vehicle
    True,                 # start cumul to zero: every vehicle leaves the depot empty
    "Capacity",
)
```

Slack is 0 because a truck cannot gain load from nowhere, and the start is fixed at 0 because it
leaves empty. The guide's four vehicles each carry 15, and its 16 demands add up to exactly 60:

```text
Objective: 6208
vehicle 0: 0 Load(0) -> 7 Load(0) -> 3 Load(8) -> 4 Load(10) -> 1 Load(14) -> 0 Load(15)
vehicle 1: 0 Load(0) -> 14 Load(0) -> 16 Load(4) -> 10 Load(12) -> 9 Load(14) -> 0 Load(15)
vehicle 2: 0 Load(0) -> 12 Load(0) -> 11 Load(2) -> 15 Load(3) -> 13 Load(11) -> 0 Load(15)
vehicle 3: 0 Load(0) -> 8 Load(0) -> 2 Load(8) -> 6 Load(9) -> 5 Load(13) -> 0 Load(15)
```

Read the loads closely. Vehicle 0 arrives at node 7 with `Load(0)`, and node 7's demand of 8 only
shows at node 3. The cumul is the value **on arrival**: the transit of a stop is added on the arc
that leaves it. So the cumul at a stop is everything picked up before it, and the cumul at the
end is the route's whole load, 15 for every vehicle here. The guide's own printer adds each
stop's demand itself and shows the load after the stop; both readings are right once you know
which one you are printing. The total, 6,208 m, is the one the CVRP guide prints. (This copy stops
its search after 100 solutions instead of the guide's one second, so the result is the same on
every run; lesson 4.8.5 explains why.)

The Valley model adds a "Kits" dimension the same way, with a callback that returns a site's kits:

```python
def kits(from_index):
    return places[manager.IndexToNode(from_index)].kits
kits_index = routing.RegisterUnaryTransitCallback(kits)
# Kits: cumulative kits used, at most KITS_PER_TRUCK for each crew.
routing.AddDimensionWithVehicleCapacity(kits_index, 0, [KITS_PER_TRUCK] * CREWS, True, "Kits")
```

Every crew in the runs above ends with 12 kits or fewer. A model can hold as many dimensions as it
has quantities (distance, time, kits, weight), each under its own name. The CVRP guide's advice
for several kinds of load is one callback and one dimension per kind, each with a unique name:
`AddDimension` returns `False` and creates nothing when the name is already taken.

<!-- practice 2 -->

## The Search Does Not Prove That a Fleet Is Too Small

The Valley sites need 33 kits. With two crews the trucks carry 24, so no plan exists. A MIP solver
would prove the model infeasible and say so (lesson 4.2.2 reads MathOpt's termination reasons). The routing search is a heuristic,
and a heuristic that finds nothing has not proved there is nothing to find:

```python
needed, carried = sum(s.kits for s in places), CREWS * KITS_PER_TRUCK
print(f"kits needed {needed}, kits carried {carried}: {'cannot fit' if needed > carried else 'may fit'}")
parameters.time_limit.FromSeconds(2)    # the CVRP guide's advice: an unsolvable search can run for a long time
solution = routing.SolveWithParameters(parameters)
status = routing_enums_pb2.RoutingSearchStatus.Value.Name(routing.status())
```

```text
kits needed 33, kits carried 24: cannot fit
solution: None, status: ROUTING_FAIL_TIMEOUT
```

The solve returns `None`, and `routing.status()` says why it stopped: `ROUTING_FAIL_TIMEOUT`,
"time limit reached before finding a solution", not "proven infeasible". Two habits follow:

- **Check the arithmetic before you solve.** Total demand against total capacity is one line of
  Python, and it gives the planner a reason ("2 crews carry 24 kits, the day needs 33") that the
  solver cannot.
- **Always set a limit** when routes might not exist. The CVRP guide warns that an unsolvable
  problem can keep the search running for a long time. Lesson 4.8.4 shows the other remedy: make
  some visits optional, so a plan always exists.

## The Model

The capacitated Valley model `valley_crews.py` builds, in one place. Lesson 4.8.1 gave the
successor variables and routes; this lesson added the vehicles, the Drive and Kits dimensions and
the span term. It is a vehicle routing model; the routing library searches it with heuristics.

**Sets.** $`N`$ the nodes, node 0 the yard and 1 to 18 the Valley sites; $`V`$ the crews,
$`|V| = 3`$; $`I`$ the solver's indices: one per site, a start $`s_v`$ and an end $`e_v`$ per crew.

**Parameters.** $`c_{ab}`$ drive minutes from node $`a`$ to $`b`$ (integers, fictional);
$`k_a`$ the kits site $`a`$ uses ($`k_0 = 0`$); $`K_v = 12`$ the kits crew $`v`$'s truck
carries; $`D = 150`$ the most minutes a crew may drive; $`\beta`$ the span coefficient (0 or
100).

**Variables.** $`\text{next}_i \in I`$ for each non-end index (the successor);
$`\text{vehicle}_i \in V`$; $`0 \le \text{drive}_i \le D`$ and $`0 \le \text{load}_i \le
K_{\text{vehicle}_i}`$ for every index, the cumuls of the Drive and Kits dimensions, all integer.

**Objective.**

```math
\min \; \sum_{i \in I \setminus \{e_v\}} c_{\text{node}(i),\, \text{node}(\text{next}_i)}
\; + \; \beta \left( \max_{v \in V} \text{drive}_{e_v} - \min_{v \in V} \text{drive}_{s_v} \right)
```

**Constraints.**

```math
\begin{aligned}
& \text{next}, \text{vehicle} \text{ form one route per crew from } s_v \text{ to } e_v, \text{ every site on one route} && && \text{(routes, lesson 4.8.1)} \\
& \text{drive}_{s_v} = 0, \quad \text{load}_{s_v} = 0 && \forall v \in V && \text{(start at zero)} \\
& \text{drive}_{\text{next}_i} = \text{drive}_i + c_{\text{node}(i),\, \text{node}(\text{next}_i)} && \forall i \in I \setminus \{e_v\} && \text{(Drive dimension)} \quad \leftarrow \text{this lesson} \\
& \text{load}_{\text{next}_i} = \text{load}_i + k_{\text{node}(i)} && \forall i \in I \setminus \{e_v\} && \text{(Kits dimension)} \quad \leftarrow \text{this lesson} \\
& \text{drive}_i \le D, \quad \text{load}_i \le K_{\text{vehicle}_i} && \forall i \in I && \text{(capacities)} \quad \leftarrow \text{this lesson}
\end{aligned}
```

| Label | Code in `valley_crews.py` |
| --- | --- |
| Drive dimension, $`\text{drive}_i \le D`$, start at zero | `AddDimension(drive_index, 0, MAX_DRIVE, True, "Drive")` |
| span term $`\beta`$ | `SetGlobalSpanCostCoefficient(span_coefficient)` |
| Kits dimension, $`\text{load}_i \le K_v`$, start at zero | `AddDimensionWithVehicleCapacity(kits_index, 0, [KITS_PER_TRUCK] * CREWS, True, "Kits")` |

## Summary

- **One index manager serves the whole fleet.** The vehicle count is the manager's second argument;
  the solver assigns sites to vehicles, and an unused vehicle drives start to end.
- **A dimension accumulates a quantity along each route:** cumul at the next stop = cumul + transit
  + slack, with every cumul at most the capacity. A dimension is a constraint; a span coefficient
  also puts it in the objective.
- **A capacity is a dimension whose transit is the demand,** from a unary callback, with one
  capacity per vehicle. The cumul is the load on arrival.
- **The search does not prove that a fleet is too small.** It returns `None` with a failure status;
  check total demand against total capacity yourself, and set a limit.

## Reference

| Call | What it does |
| --- | --- |
| `routing.AddDimension(handle, slack_max, capacity, fix_start, name)` | a dimension with one capacity for all vehicles |
| `routing.AddDimensionWithVehicleCapacity(handle, slack_max, [cap per vehicle], fix_start, name)` | one capacity per vehicle |
| `routing.RegisterUnaryTransitCallback(f)` | registers `f(from_index)`, a transit that depends on one stop |
| `routing.GetDimensionOrDie(name)` | the dimension by name |
| `dimension.CumulVar(i)` | the quantity on arrival at index `i`; read it with `solution.Value(...)` |
| `dimension.SetGlobalSpanCostCoefficient(b)` | adds `b` × (largest end cumul − smallest start cumul) to the objective |
| `routing.IsVehicleUsed(solution, v)` | false when vehicle `v` drives start to end |
| `routing.status()` | why the search stopped (`ROUTING_SUCCESS`, `ROUTING_FAIL_TIMEOUT`, ...) |

**Further reading:** [OR-Tools: Vehicle routing problem](https://developers.google.com/optimization/routing/vrp),
[VRP with capacity constraints](https://developers.google.com/optimization/routing/cvrp),
[Routing options](https://developers.google.com/optimization/routing/routing_options) (search
statuses), and the samples [vrp_global_span.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_global_span.py)
and [vrp_capacity.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_capacity.py).

## Challenges

1. Give crew 2 a smaller truck that carries 9 kits. Predict which crew's route changes most.
2. Replace the global span with `SetSpanCostCoefficientForAllVehicles(100)`, which charges each
   route's own span. Which objective does that minimize?
3. Lower `MAX_DRIVE` until the solver stops finding routes within a time limit. Is the plan then
   truly impossible? How would you know?

## Design Note: Dimensions Are the Routing Library's Linear Rows

In a MIP, every limit is a row. In the routing library almost every limit is a dimension: one
callback for how the quantity changes on an arc, one capacity for how high it may go, and a slack
for how much it may rise on its own. Distance, time, load, crew hours and money all fit the same
shape. When a new rule arrives, the first question is: "what quantity builds up along the route,
and what bounds it?" If the answer fits, the rule is a dimension, and the solver's moves already
know how to respect it.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**vrp_global_span.py.** The OR-Tools VRP guide's example, adapted with attribution: a distance
dimension and the global span (*One Index Manager Serves the Whole Fleet*, *A Dimension
Accumulates a Quantity Along Each Route*). *Try:* Set the span coefficient to 0. Predict the total
distance and the longest route.

- Program: [vrp_global_span.py](src/vrp_global_span.py)

**vrp_capacity.py.** The OR-Tools CVRP guide's example, adapted with attribution (*A Capacity Is
a Dimension Whose Transit Is the Demand*). *Try:* Change one capacity to 14. Predict what the solver
does with a total capacity of 59 for a demand of 60, and set a time limit before you run it.

- Program: [vrp_capacity.py](src/vrp_capacity.py)

**valley_crews.py.** Three Valley crews with Drive and Kits dimensions, with and without the span
term (*A Dimension Accumulates a Quantity Along Each Route*). *Try:* Set `KITS_PER_TRUCK` to 11
(33 kits for 33 needed). Predict whether every truck ends exactly full.

- Program: [valley_crews.py](src/valley_crews.py)

**fleet_check.py.** Two crews for 33 kits: the arithmetic check and the search status (*The Search
Does Not Prove That a Fleet Is Too Small*). *Try:* Give the two crews 17 kits each. Predict the
status.

- Program: [fleet_check.py](src/fleet_check.py)

**guide_data.py.** The 17-location data the OR-Tools VRP guides share. It runs nothing itself.

- Library: [guide_data.py](src/guide_data.py)
