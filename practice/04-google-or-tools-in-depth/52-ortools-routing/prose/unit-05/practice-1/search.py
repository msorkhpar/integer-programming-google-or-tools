from __future__ import annotations

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

DEFAULT_SOLUTIONS = 200


def search_parameters(strategy: str, metaheuristic: str | None = None, solutions: int | None = None):
    """Search parameters from names, for runs that repeat: a metaheuristic that escapes local
    minima always gets a solution limit (DEFAULT_SOLUTIONS when none is given), and no run gets
    a time limit."""
    params = pywrapcp.DefaultRoutingSearchParameters()
    # TODO: the strategy, the metaheuristic and the solution limit.
    return params


if __name__ == "__main__":
    print(search_parameters("SAVINGS", "GUIDED_LOCAL_SEARCH"))
