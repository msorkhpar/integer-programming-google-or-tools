# 4.8. OR-Tools Routing

The OR-Tools routing library plans routes for vehicles that visit places: the traveling
salesperson problem, vehicle routing with capacities, time windows and service times, optional
visits with penalties, and pickup and delivery. It is not an LP or MIP solver. It keeps one
"successor" variable per stop and searches over routes with heuristics and local search. This
module teaches its API the way the OR-Tools routing guides do: the index manager, transit
callbacks, dimensions and slack, disjunctions with penalties, and search parameters. Then it plans
the inspection crews of GridCap's Valley region.

GridCap is fictional and has no map. The module's programs invent coordinates for the Valley
substations from a fixed seed, so every drive time here is made up and the same on every run.

## Contents

1. [The routing model: index manager, transit callbacks and the TSP](README_4.8.1.md)
2. [Vehicles, capacities and dimensions (CVRP)](README_4.8.2.md)
3. [Time windows and service times (VRPTW)](README_4.8.3.md)
4. [Optional visits with penalties, and pickup and delivery](README_4.8.4.md)
5. [First-solution strategies, local search and search limits](README_4.8.5.md)
