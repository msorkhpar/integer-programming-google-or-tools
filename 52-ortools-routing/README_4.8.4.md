# 4.8.4 Optional Visits With Penalties, and Pickup and Delivery

Two of the Valley's four inspection crews are called away to storm repairs, and the two that remain
cannot inspect all 18 substations in one shift. The eight urgent sites (five years or less of
predicted life) must still be done today; the ten routine ones can wait for next week, but the
planner would rather skip the ones whose failure would cost least. Lesson 4.8.2 showed what a plain
routing model does when the work does not fit: it finds nothing, and says only that it timed out.
This lesson makes the routine visits optional, at a price, so a plan always exists and the price
decides what gets skipped.

The same afternoon, a second request arrives: the portable transformer test set was left at
substation A157, and the crew inspecting A230 needs it. Some crew must collect it at A157 and carry
it to A230. That is a **pickup and delivery** pair, the second half of this lesson. The drive times
are fictional, as everywhere in this module.

## A Disjunction With a Penalty Makes a Visit Optional

The routing library's tool for "this visit may be skipped" is the **disjunction**: a set of indices
of which at most a given number (by default one) are visited. With a penalty, each index of the set
that is left out adds the penalty to the objective. A disjunction holding a single index is exactly
"visit this site, or pay to skip it". The OR-Tools dropped-visits guide makes all 16 of its
locations optional this way:

```python
# Allow to drop nodes: one disjunction per location, each holding that one location.
penalty = 1000
for node in range(1, len(distance_matrix)):
    routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
```

Three rules come from `AddDisjunction`'s docstring:

- **The list holds indices, not nodes**, so convert with `NodeToIndex`.
- **The depot, and every vehicle's start and end, cannot be in a disjunction.** The loop starts at
  node 1 for that reason.
- **A site with no disjunction is mandatory.** That is how the Valley model keeps the urgent sites:
  it gives a disjunction to the routine sites only.

The docstring adds a fourth rule: **a negative penalty makes the disjunction mandatory**. The
penalty must be positive for the visit to be optional; a negative one forces the visit, so
`AddDisjunction([index], -1)` keeps the site just as leaving it out of every disjunction does.
That is handy when the penalties come from data and a must-visit site is marked with a negative
number. `negative_penalty.py` runs the two-crew Valley day of the next section twice, with A183's
penalty at 10,000 and at -1:

```python
for label, a183 in (("A183 penalty 10000", 10_000), ("A183 penalty -1", -1)):
    penalty = lambda site: a183 if site.name == "A183" else 10_000
```

```text
A183 penalty 10000: objective 70176, dropped 7: A091, A133, A149, A183, A281, A302, A344
  crew 0: A348 > A064 > A106 > A308 > A087  back 14:17
  crew 1: A157 > A378 > A136 > A096 > A230 > A305  back 15:50
A183 penalty -1: objective 70176, dropped 7: A064, A091, A133, A281, A302, A305, A344
  crew 0: A378 > A157 > A348 > A136 > A230  back 14:31
  crew 1: A183 > A149 > A096 > A106 > A308 > A087  back 14:17
```

With a penalty of 10,000, A183 is among the seven dropped sites; with -1 it is on crew 1's route,
and seven other routine sites are dropped instead.

```python
if penalty is not None:
    for node in range(1, len(places)):
        if not places[node].urgent:                       # urgent sites stay mandatory
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty(places[node]))
```

The guide's data has demands that add up to 70 for four vehicles of capacity 15 (60 in all), so at
least 10 units of demand must be dropped:

```text
Objective: 7548
Dropped nodes: 15 16 (demand 16)
vehicle 0: 0 -> 8 -> 14 -> 9 -> 0  load 15
vehicle 1: 0 -> 1 -> 3 -> 4 -> 11 -> 12 -> 0  load 13
vehicle 2: 0 -> 7 -> 13 -> 0  load 14
vehicle 3: 0 -> 5 -> 6 -> 2 -> 10 -> 0  load 12
distance 5548 + 2 x 1000 = 7548
```

The objective is the distance plus 1,000 per dropped node. The guide's page shows a different
answer, nodes 6 and 15 dropped for 7,936. Its program stops the search after one second; this copy
stops it after 100 solutions. Both are plans the model accepts, from searches that ran for
different lengths, and how a search is stopped is lesson 4.8.5's subject.

## The Penalty Decides What Gets Dropped

The penalty is the price of skipping a visit, in the objective's units (here meters or drive
minutes). The solver drops a site whenever dropping it saves more than its penalty, and that one
fact sets the rule for choosing penalties. The dropped-visits guide states it: a penalty larger
than the sum of all arc costs means dropping a visit can never pay for itself, so the solver drops
only what it must to make the plan feasible. A smaller penalty lets it drop a visit just because
it is out of the way.

`valley_drops.py` runs the Valley day four ways, with vans of 12 kits:

```python
policies = [
    ("two crews, penalty 10000 each", 2, lambda site: 10_000),
    ("two crews, penalty cof // 10", 2, lambda site: site.cof // 10),
    ("three crews, penalty 10000 each", 3, lambda site: 10_000),
    ("three crews, penalty cof // 100", 3, lambda site: site.cof // 100),
]
```

```text
all arcs of the drive matrix add up to 8334 minutes
low-priority sites (cof $k): A064 523, A091 2577, A096 2505, A133 291, A149 661, A183 2978, A281 2241, A302 210, A305 3516, A344 1843
two crews, penalty 10000 each: objective 70176 = drive 176 + penalties 70000
  dropped 7: A091, A133, A149, A183, A281, A302, A344
  crew 0: A348 > A064 > A106 > A308 > A087  back 14:17
  crew 1: A157 > A378 > A136 > A096 > A230 > A305  back 15:50
two crews, penalty cof // 10: objective 1062 = drive 229 + penalties 833
  dropped 7: A064, A091, A133, A149, A281, A302, A344
  crew 0: A305 > A087 > A230 > A136 > A378  back 15:51
  crew 1: A157 > A348 > A106 > A308 > A096 > A183  back 15:04
three crews, penalty 10000 each: objective 283 = drive 283 + penalties 0
  dropped 0: none
  crew 0: A096 > A106 > A302 > A281 > A305 > A344 > A133 > A183  back 14:53
  crew 1: A378 > A157 > A149 > A348 > A136  back 13:22
  crew 2: A087 > A064 > A091 > A308 > A230  back 15:12
three crews, penalty cof // 100: objective 244 = drive 215 + penalties 29
  dropped 3: A064, A281, A302
  crew 0: A087 > A305 > A344 > A133 > A183  back 12:25
  crew 1: A378 > A157 > A149 > A348 > A136  back 13:22
  crew 2: A096 > A106 > A091 > A308 > A230  back 15:12
```

Read the runs as business policies:

- **Penalty 10,000 for every routine site** is above the 8,334-minute sum of all arcs, so no drop
  pays for itself in driving. With two crews, all eight urgent sites are kept (they have no
  disjunction), and seven routine ones are dropped. With equal penalties, the solver has no reason to prefer one routine
  site over another, so which seven go is decided by geography: it kept A064, A096 and A305.
- **Penalty proportional to the consequence of failure (cof)** says what the planner means:
  skipping a transformer whose failure costs $3.5M is worse than skipping one that costs $0.2M. Seven
  sites are still dropped, but now A183 (cof 2,978) is kept and A064 (cof 523) is dropped.
- **A penalty that is too small** (cof // 100, 2 to 35 minutes) breaks the plan in the other
  direction. With three crews and a penalty of 10,000, the solver visits all 18 sites in 283 drive
  minutes, so three crews can do the whole day. With cof // 100 it drops A064, A281 and A302 anyway,
  for penalties of 5, 22 and 2 minutes (29 in all), because the plan without them drives 215
  minutes: 68 minutes saved for 29 paid. Those three transformers go uninspected to save fuel.

A penalty is a trade-off rate between two things the objective adds up. Put both in the same units,
check that the largest saving a drop could bring cannot exceed the penalty of a site you must not
lose, and when nothing may be skipped, leave the site out of every disjunction.

## A Dropped Visit Is an Index That Points to Itself

A dropped site is on no route, and the routing model encodes that by making it its own successor:
$`\text{next}_i = i`$. So you find dropped visits by testing every index that is neither a start
nor an end, as the guide's printer does:

```python
def dropped(manager, routing, solution) -> list[int]:
    """Nodes on no route: a dropped visit's next variable points back to itself."""
    return [manager.IndexToNode(index) for index in range(routing.Size())
            if not routing.IsStart(index) and not routing.IsEnd(index)
            and solution.Value(routing.NextVar(index)) == index]
```

The start test matters: a start index is never a visit, even when its vehicle is unused (then it
points to its end). The ends lie past `routing.Size()` (lesson 4.8.1's index table), so the loop
never reaches them; the `IsEnd` test only makes the intent plain.

The penalty a plan paid is the sum of its dropped sites' penalties, and the objective minus that sum
is the driving. `valley_drops.py` prints the split on every line ("drive 229 + penalties 833"), and
a planner should get the same split: a total of 1,062 means little until you know how much of it is
fuel and how much is risk left in the field.

<!-- practice 1 -->

## Pickup and Delivery Is a Pair, a Same-Vehicle Row and an Order Row

The test set must be collected at A157 and taken to A230. The pickup and the delivery are two visits
with two rules between them: **the same crew** does both, and it reaches **the pickup first**. The
OR-Tools pickup-and-delivery guide writes each rule as one constraint, plus a call that tells the
search the two visits belong together:

```python
for pickup_node, delivery_node in pickups_deliveries:
    pickup_index = manager.NodeToIndex(pickup_node)
    delivery_index = manager.NodeToIndex(delivery_node)
    routing.AddPickupAndDelivery(pickup_index, delivery_index)
    # The same vehicle does both stops ...
    routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
    # ... and reaches the pickup first (the distance driven so far is smaller there).
    routing.solver().Add(distance_dimension.CumulVar(pickup_index) <= distance_dimension.CumulVar(delivery_index))
```

- `routing.solver()` is the constraint-programming solver under the routing model, and `Add` posts
  a constraint on its variables directly. This is how you write a rule that no dimension or
  disjunction expresses.
- `routing.VehicleVar(i)` is the vehicle that visits index $`i`$; equal vehicle variables put both
  stops on one route.
- The order row compares cumuls of a dimension that only grows along a route (distance driven), so
  "smaller cumul" means "earlier on the route". A time dimension works the same way.
- `AddPickupAndDelivery(pickup, delivery)` declares the pair. Its docstring says it helps the search,
  especially local search, which then moves both stops together.

The guide's eight items and four vehicles, from this module's adapted copy:

```text
Objective: 226116
vehicle 0: 0 -> 13 -> 15 -> 11 -> 12 -> 0  (1552 m)
vehicle 1: 0 -> 5 -> 2 -> 10 -> 16 -> 14 -> 9 -> 0  (2192 m)
vehicle 2: 0 -> 4 -> 3 -> 0  (1392 m)
vehicle 3: 0 -> 7 -> 1 -> 6 -> 8 -> 0  (1780 m)
total 6916 m, longest 2192 m, 100 x 2192 + 6916 = 226116
```

Each pair from the data sits on one route in order: [1, 6] on vehicle 3, [2, 10] and [5, 9] on
vehicle 1, [4, 3] on vehicle 2. The search here starts from `PARALLEL_CHEAPEST_INSERTION`, the
guide's choice for this problem (lesson 4.8.5 compares strategies).

Which of the three calls does what? `valley_test_set.py` builds the Valley pair three ways and asks
the model to accept or refuse three hand-built plans. `routing.ReadAssignmentFromRoutes(routes,
True)` takes one list of nodes per vehicle (depot left out) and returns `None` when the plan breaks
a rule, which makes it a direct test of a model:

```python
for variant, flags in variants.items():
    print(f"AddPickupAndDelivery with {variant}:")
    for label, plan in plans.items():
        manager, routing = build(**flags)
        accepted = routing.ReadAssignmentFromRoutes(plan, True) is not None
```

```text
AddPickupAndDelivery with both rows:
  one crew, pickup then delivery         accepted
  one crew, delivery then pickup         refused
  pickup by crew 0, delivery by crew 1   refused
AddPickupAndDelivery with same-vehicle row left out:
  one crew, pickup then delivery         accepted
  one crew, delivery then pickup         refused
  pickup by crew 0, delivery by crew 1   accepted
AddPickupAndDelivery with order row left out:
  one crew, pickup then delivery         accepted
  one crew, delivery then pickup         refused
  pickup by crew 0, delivery by crew 1   refused
```

The result in OR-Tools 9.15: `AddPickupAndDelivery` by itself already refused the delivery before
the pickup, but it **accepted a plan in which crew 0 collects the test set and crew 1 delivers it**,
which no crew could carry out. Only the same-vehicle row refuses that. So write both rows, as the
guide does: the order row states the rule in your model rather than leaving it to a declaration,
and the same-vehicle row is the one the plan cannot do without.

The solved Valley plan:

```text
objective 851
  crew 0: YARD > A348 > A136 > A106 > A308 > A087 > YARD
  crew 1: YARD > A157 > A378 > A230 > YARD
```

Crew 1 collects the test set at A157 and delivers it at A230, two stops later. (The objective
includes a span coefficient of 10 on the Drive dimension, so it is not the drive time alone.)

<!-- practice 2 -->

## The Model

The Valley model with optional visits that `valley_model.build` makes when it gets a `penalty`, and
the pickup-and-delivery rows of `valley_test_set.py`. Lessons 4.8.1 to 4.8.3 gave routes, Kits and
Time; this lesson added the disjunctions and the pair. It is a vehicle routing model, searched by
the routing library's heuristics.

**Sets.** $`N`$ the nodes, node 0 the yard and 1 to 18 the sites; $`U \subseteq N`$ the urgent
sites; $`R = N \setminus (U \cup \{0\})`$ the routine sites; $`V`$ the crews; $`I`$ the indices;
$`P`$ the pickup-delivery pairs $`(p, d)`$ (one pair, A157 to A230, in `valley_test_set.py`).

**Parameters.** As in lesson 4.8.3 ($`c_{ab}`$, $`\text{service}_a`$, $`[a_i, b_i]`$, $`H`$,
$`W`$, $`k_a`$, $`K`$), plus $`\pi_i > 0`$, the penalty for skipping routine site $`i`$.

**Variables.** As in lesson 4.8.3, plus $`\text{active}_i \in \{0, 1\}`$ for each site index: 1
if a route visits it. A site with $`\text{active}_i = 0`$ has $`\text{next}_i = i`$.

**Objective.**

```math
\min \; \sum_{i \in I \setminus \{e_v\},\ \text{active}_i = 1} c_{\text{node}(i),\, \text{node}(\text{next}_i)}
\; + \; \sum_{i \in R} \pi_i \,(1 - \text{active}_i)
```

**Constraints.**

```math
\begin{aligned}
& \text{active}_i = 1 && \forall i \in U && \text{(urgent: no disjunction)} \\
& \text{active}_i \le 1 && \forall i \in R && \text{(disjunction}_i) \quad \leftarrow \text{this lesson} \\
& \text{next}_i = i \iff \text{active}_i = 0 && \forall i \in R && \text{(dropped points to itself)} \quad \leftarrow \text{this lesson} \\
& \text{vehicle}_p = \text{vehicle}_d && \forall (p, d) \in P && \text{(same crew)} \quad \leftarrow \text{this lesson} \\
& \text{drive}_p \le \text{drive}_d && \forall (p, d) \in P && \text{(pickup first)} \quad \leftarrow \text{this lesson} \\
& \text{routes, Time with windows and waiting, Kits} && && \text{(lessons 4.8.1 to 4.8.3, active sites only)}
\end{aligned}
```

| Label | Code |
| --- | --- |
| disjunction$`_i`$, $`\pi_i`$ | `routing.AddDisjunction([manager.NodeToIndex(node)], penalty(places[node]))` |
| urgent | no `AddDisjunction` call for the site |
| same crew | `routing.solver().Add(routing.VehicleVar(pickup) == routing.VehicleVar(delivery))` |
| pickup first | `routing.solver().Add(drive_dim.CumulVar(pickup) <= drive_dim.CumulVar(delivery))` |
| the pair, for the search | `routing.AddPickupAndDelivery(pickup, delivery)` |

## Summary

- **A disjunction with a penalty makes a visit optional.** `AddDisjunction([index], penalty)` per
  optional site; a site with no disjunction, or with a negative penalty, stays mandatory; the depot
  can never be in one.
- **The penalty decides what gets dropped.** The solver drops a site when the saving exceeds the
  penalty. Above the sum of all arc costs, it drops only what it must; proportional to value, it
  drops the least valuable; too small, it drops sites it could have visited.
- **A dropped visit is an index that points to itself.** Test `solution.Value(routing.NextVar(i))
  == i` for every index that is neither a start nor an end, and report penalties apart from driving.
- **Pickup and delivery is a pair, a same-vehicle row and an order row.** In OR-Tools 9.15,
  `AddPickupAndDelivery` alone accepted a pair split across two vehicles; the same-vehicle row
  refuses it.

## Reference

| Call | What it does |
| --- | --- |
| `routing.AddDisjunction([i], penalty)` | visit `i` or pay `penalty`; a negative penalty makes it mandatory |
| `routing.AddDisjunction([i, j, k], penalty, max_cardinality)` | visit at most `max_cardinality` of the set; pay per missing one |
| `solution.Value(routing.NextVar(i)) == i` | index `i` was dropped |
| `routing.AddPickupAndDelivery(p, d)` | declares a pickup-delivery pair for the search |
| `routing.VehicleVar(i)` | the vehicle that visits index `i` |
| `routing.solver().Add(constraint)` | posts any constraint on the routing variables |
| `routing.ReadAssignmentFromRoutes(routes, True)` | a hand-built plan as an assignment, or `None` if the model refuses it |

**Further reading:** [OR-Tools: VRP with dropped visits](https://developers.google.com/optimization/routing/penalties),
[Pickups and deliveries](https://developers.google.com/optimization/routing/pickup_delivery),
[Common routing tasks](https://developers.google.com/optimization/routing/routing_tasks) (initial
routes), and the samples [vrp_drop_nodes.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_drop_nodes.py)
and [vrp_pickup_delivery.py](https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_pickup_delivery.py).

## Challenges

1. In `valley_drops.py`, give the urgent sites a disjunction too, with a penalty of 100,000. Predict
   what changes with two crews.
2. Two substations sit on the same feeder, and inspecting either one is enough. Write it as one
   disjunction of two indices.
3. The test set must be delivered before 11:00. Which dimension and which call express that?

## Design Note: Penalties Turn "Infeasible" Into "Here Is What It Costs"

A model with hard visits answers a short fleet with nothing (lesson 4.8.2). A model with penalties
always has a plan (drop everything is one), and it answers a different, better question: "with the
crews I have, what is the least painful set of visits to postpone?" The price of that answer is
that the penalties are now part of the model, and a planner must agree to them. Write them in
business terms (here, a share of the consequence of failure), show the dropped list next to the
routes, and treat "seven sites postponed" as a result to explain, not a detail.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**vrp_drop_nodes.py.** The OR-Tools dropped-visits guide's example, adapted with attribution (*A
Disjunction With a Penalty Makes a Visit Optional*). *Try:* Set the penalty to 100. Predict whether
more nodes are dropped.

- Program: [vrp_drop_nodes.py](src/vrp_drop_nodes.py)

**valley_drops.py.** Optional routine inspections in four runs: three penalty policies (10,000
per site, cof // 10, cof // 100), with two crews or three (*The Penalty
Decides What Gets Dropped*, *A Dropped Visit Is an Index That Points to Itself*). *Try:* Use
`site.cof` as the penalty with three crews. Predict the number of drops.

- Program: [valley_drops.py](src/valley_drops.py)

**negative_penalty.py.** The two-crew day with A183's penalty at 10,000 and at -1 (*A Disjunction
With a Penalty Makes a Visit Optional*). *Try:* Give A305 a penalty of -1 as well. Predict whether
the objective changes.

- Program: [negative_penalty.py](src/negative_penalty.py)

**vrp_pickup_delivery.py.** The OR-Tools pickup-and-delivery guide's example, adapted with
attribution (*Pickup and Delivery Is a Pair, a Same-Vehicle Row and an Order Row*). *Try:* Remove
the same-vehicle row and run again. Predict whether every pair still shares a vehicle.

- Program: [vrp_pickup_delivery.py](src/vrp_pickup_delivery.py)

**valley_test_set.py.** The test-set pair on the Valley crews, and three hand-built plans checked
against three versions of the model (*Pickup and Delivery Is a Pair, a Same-Vehicle Row and an
Order Row*). *Try:* Add a second pair, A348 to A136. Predict which crew takes it.

- Program: [valley_test_set.py](src/valley_test_set.py)
