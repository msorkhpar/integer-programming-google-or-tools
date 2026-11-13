from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

DEFAULT_SOLUTIONS = 200


def search_parameters(strategy: str, metaheuristic: str | None = None, solutions: int | None = None):
    """Search parameters from names, for runs that repeat: a metaheuristic that escapes local
    minima always gets a solution limit (DEFAULT_SOLUTIONS when none is given), and no run gets
    a time limit."""
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = getattr(routing_enums_pb2.FirstSolutionStrategy, strategy)
    if metaheuristic is not None:
        params.local_search_metaheuristic = getattr(routing_enums_pb2.LocalSearchMetaheuristic, metaheuristic)
    if solutions is not None:
        params.solution_limit = solutions
    elif metaheuristic not in (None, "GREEDY_DESCENT"):
        params.solution_limit = DEFAULT_SOLUTIONS
    return params


if __name__ == "__main__":
    print(search_parameters("SAVINGS", "GUIDED_LOCAL_SEARCH"))
