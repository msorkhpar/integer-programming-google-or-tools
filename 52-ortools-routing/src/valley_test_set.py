"""Pickup and delivery: a crew collects the portable test set at A157 and brings it to A230.

Adapted onto GridCap from the OR-Tools example vrp_pickup_delivery.py,
https://github.com/google/or-tools/blob/v9.15/ortools/constraint_solver/samples/vrp_pickup_delivery.py
Two crews, the eight urgent sites, drive minutes only. The drive times are fictional.
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import drive_minutes, sites

places = sites(urgent_only=True)
minutes = drive_minutes(places)
node = {s.name: n for n, s in enumerate(places)}
PICKUP, DELIVERY = node["A157"], node["A230"]


def build(same_vehicle_row: bool = True, order_row: bool = True):
    manager = pywrapcp.RoutingIndexManager(len(places), 2, 0)
    routing = pywrapcp.RoutingModel(manager)
    drive_index = routing.RegisterTransitCallback(
        lambda i, j: minutes[manager.IndexToNode(i)][manager.IndexToNode(j)])
    routing.SetArcCostEvaluatorOfAllVehicles(drive_index)
    routing.AddDimension(drive_index, 0, 480, True, "Drive")
    drive_dim = routing.GetDimensionOrDie("Drive")
    drive_dim.SetGlobalSpanCostCoefficient(10)

    pickup, delivery = manager.NodeToIndex(PICKUP), manager.NodeToIndex(DELIVERY)
    routing.AddPickupAndDelivery(pickup, delivery)
    if same_vehicle_row:
        routing.solver().Add(routing.VehicleVar(pickup) == routing.VehicleVar(delivery))
    if order_row:
        routing.solver().Add(drive_dim.CumulVar(pickup) <= drive_dim.CumulVar(delivery))
    return manager, routing


manager, routing = build()
parameters = pywrapcp.DefaultRoutingSearchParameters()
parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
solution = routing.SolveWithParameters(parameters)
print(f"objective {solution.ObjectiveValue()}")
for crew in range(2):
    index, names = routing.Start(crew), []
    while not routing.IsEnd(index):
        names.append(places[manager.IndexToNode(index)].name)
        index = solution.Value(routing.NextVar(index))
    print(f"  crew {crew}: {' > '.join(names + ['YARD'])}")

# Hand-built plans, checked by the model: ReadAssignmentFromRoutes returns None for a plan it refuses.
others = [n for n in range(1, len(places)) if n not in (PICKUP, DELIVERY)]
plans = {
    "one crew, pickup then delivery": [[PICKUP, DELIVERY] + others[:3], others[3:]],
    "one crew, delivery then pickup": [[DELIVERY, PICKUP] + others[:3], others[3:]],
    "pickup by crew 0, delivery by crew 1": [[PICKUP] + others[:3], others[3:] + [DELIVERY]],
}
variants = {"both rows": {}, "same-vehicle row left out": {"same_vehicle_row": False},
            "order row left out": {"order_row": False}}
for variant, flags in variants.items():
    print(f"AddPickupAndDelivery with {variant}:")
    for label, plan in plans.items():
        manager, routing = build(**flags)
        accepted = routing.ReadAssignmentFromRoutes(plan, True) is not None
        print(f"  {label:38} {'accepted' if accepted else 'refused'}")
