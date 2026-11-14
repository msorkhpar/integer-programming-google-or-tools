"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.constraint_solver import routing_enums_pb2

from search import search_parameters

FIRST = routing_enums_pb2.FirstSolutionStrategy
META = routing_enums_pb2.LocalSearchMetaheuristic

for args in (("SAVINGS",), ("PATH_CHEAPEST_ARC", "TABU_SEARCH"), ("CHRISTOFIDES", "GUIDED_LOCAL_SEARCH", 25),
             ("PATH_CHEAPEST_ARC", "GREEDY_DESCENT")):
    params = search_parameters(*args)
    print(f"{args}: strategy {FIRST.Value.Name(params.first_solution_strategy)},"
          f" metaheuristic {META.Value.Name(params.local_search_metaheuristic)},"
          f" solution limit {params.solution_limit}, time limit set {params.HasField('time_limit')}")
