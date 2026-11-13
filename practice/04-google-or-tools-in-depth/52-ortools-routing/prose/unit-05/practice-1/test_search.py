from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from search import search_parameters

FIRST = routing_enums_pb2.FirstSolutionStrategy
META = routing_enums_pb2.LocalSearchMetaheuristic
UNLIMITED = 2**63 - 1      # the default solution_limit

# A laundry's two vans and seven hotels, not the lesson's substations.
DISTANCE = [
    [0, 7, 9, 12, 6, 10, 8, 11],
    [7, 0, 4, 8, 9, 13, 10, 6],
    [9, 4, 0, 5, 11, 9, 12, 7],
    [12, 8, 5, 0, 10, 6, 9, 4],
    [6, 9, 11, 10, 0, 5, 3, 12],
    [10, 13, 9, 6, 5, 0, 4, 8],
    [8, 10, 12, 9, 3, 4, 0, 10],
    [11, 6, 7, 4, 12, 8, 10, 0],
]


def solve(params):
    manager = pywrapcp.RoutingIndexManager(len(DISTANCE), 2, 0)
    routing = pywrapcp.RoutingModel(manager)
    handle = routing.RegisterTransitCallback(lambda i, j: DISTANCE[manager.IndexToNode(i)][manager.IndexToNode(j)])
    routing.SetArcCostEvaluatorOfAllVehicles(handle)
    routing.AddDimension(handle, 0, 40, True, "Distance")
    solution = routing.SolveWithParameters(params)
    plan = []
    for van in range(2):
        index, stops = routing.Start(van), []
        while not routing.IsEnd(index):
            stops.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        plan.append(stops)
    return solution.ObjectiveValue(), plan, routing.status()


def test_names_become_the_search_settings():
    params = search_parameters("SAVINGS", "GUIDED_LOCAL_SEARCH", 50)
    assert params.first_solution_strategy == FIRST.SAVINGS
    assert params.local_search_metaheuristic == META.GUIDED_LOCAL_SEARCH
    assert params.solution_limit == 50


def test_a_run_with_a_solution_limit_repeats():
    params = search_parameters("PATH_CHEAPEST_ARC", "GUIDED_LOCAL_SEARCH", 100)
    assert params.local_search_metaheuristic == META.GUIDED_LOCAL_SEARCH
    first, again = solve(params), solve(params)
    assert first == again
    assert first[2] == routing_enums_pb2.RoutingSearchStatus.ROUTING_SUCCESS


def test_a_metaheuristic_without_a_count_gets_the_default_count():
    params = search_parameters("PATH_CHEAPEST_ARC", "TABU_SEARCH")
    assert params.local_search_metaheuristic == META.TABU_SEARCH
    assert params.solution_limit == 200


def test_no_run_gets_a_time_limit():
    params = search_parameters("SAVINGS", "SIMULATED_ANNEALING", 30)
    assert params.solution_limit == 30
    assert not params.HasField("time_limit")


def test_greedy_descent_runs_to_its_local_minimum():
    params = search_parameters("PATH_CHEAPEST_ARC", "GREEDY_DESCENT")
    assert params.local_search_metaheuristic == META.GREEDY_DESCENT
    assert params.solution_limit == UNLIMITED
