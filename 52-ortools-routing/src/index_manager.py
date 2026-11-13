"""What the index manager does: the solver's indices next to your node numbers."""

from ortools.constraint_solver import pywrapcp


def index_table(num_nodes: int, num_vehicles: int, depot: int) -> None:
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)
    print(f"{num_nodes} nodes, {num_vehicles} vehicle(s), depot {depot}: "
          f"routing.Size() = {routing.Size()}, {routing.Size() + num_vehicles} indices in all")
    for index in range(routing.Size() + num_vehicles):
        role = (f"start of vehicle {routing.VehicleIndex(index)}" if routing.IsStart(index)
                else f"end of vehicle {routing.VehicleIndex(index)}" if routing.IsEnd(index) else "a visit")
        print(f"  index {index:2}  node {manager.IndexToNode(index)}  {role}")


index_table(5, 1, 0)
index_table(5, 2, 0)
index_table(5, 1, 3)

manager = pywrapcp.RoutingIndexManager(5, 2, 0)
print("NodeToIndex(3) =", manager.NodeToIndex(3), "  NodeToIndex(0) =", manager.NodeToIndex(0))
