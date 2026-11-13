"""The module 52 examples: the Valley instance, its routes, and the rules each lesson adds."""

from dataclasses import replace
from itertools import permutations

import pytest
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from valley import SHIFT, drive_minutes, sites
from valley_model import build, dropped, parameters, routes


@pytest.fixture(scope="module")
def places():
    return sites()


def test_the_instance_is_the_same_on_every_run(places):
    assert [s.name for s in places] == [s.name for s in sites()]
    assert drive_minutes(places) == drive_minutes(sites())
    assert len(places) == 19 and sum(s.urgent for s in places[1:]) == 8
    assert sum(s.kits for s in places) == 33


def test_the_tsp_route_matches_brute_force():
    urgent = sites(urgent_only=True)
    minutes = drive_minutes(urgent)
    manager = pywrapcp.RoutingIndexManager(len(urgent), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    callback = routing.RegisterTransitCallback(lambda i, j: minutes[manager.IndexToNode(i)][manager.IndexToNode(j)])
    routing.SetArcCostEvaluatorOfAllVehicles(callback)
    solution = routing.SolveWithParameters(parameters())
    best = min(sum(minutes[a][b] for a, b in zip((0, *order), (*order, 0)))
               for order in permutations(range(1, len(urgent))))
    assert solution.ObjectiveValue() == best == 106


def test_every_crew_keeps_its_windows_kits_and_shift(places):
    manager, routing = build(places, crews=4, kits_per_truck=9)
    solution = routing.SolveWithParameters(parameters())
    time_dim = routing.GetDimensionOrDie("Time")
    plan = routes(manager, routing, solution)
    assert sorted(n for crew in plan for n in crew) == list(range(1, len(places)))
    for crew, nodes in enumerate(plan):
        assert sum(places[n].kits for n in nodes) <= 9
        assert solution.Min(time_dim.CumulVar(routing.End(crew))) <= SHIFT
        for n in nodes:
            arrive = solution.Min(time_dim.CumulVar(manager.NodeToIndex(n)))
            assert places[n].window[0] <= arrive <= places[n].window[1]


def test_drops_keep_every_urgent_site_and_the_objective_adds_the_penalties(places):
    manager, routing = build(places, crews=2, kits_per_truck=12, penalty=lambda s: 10_000)
    solution = routing.SolveWithParameters(parameters())
    skipped = dropped(manager, routing, solution)
    assert skipped and not any(places[n].urgent for n in skipped)
    minutes = drive_minutes(places)
    drive = sum(minutes[a][b] for crew in routes(manager, routing, solution) for a, b in zip([0, *crew], [*crew, 0]))
    assert solution.ObjectiveValue() == drive + 10_000 * len(skipped)


def test_a_solution_limit_repeats_and_guided_local_search_improves(places):
    def cost(metaheuristic, limit):
        manager, routing = build(places, crews=4, kits_per_truck=9)
        solution = routing.SolveWithParameters(parameters("PATH_CHEAPEST_ARC", metaheuristic, limit))
        return solution.ObjectiveValue(), routes(manager, routing, solution)

    first, again = cost("GUIDED_LOCAL_SEARCH", 300), cost("GUIDED_LOCAL_SEARCH", 300)
    assert first == again
    assert first[0] < cost("GREEDY_DESCENT", None)[0]


def test_a_plan_that_breaks_a_window_is_refused(places):
    node = {s.name: n for n, s in enumerate(places)}
    yesterday = [[node[n] for n in crew] for crew in
                 [["A064", "A106", "A302", "A281", "A308"], ["A087", "A230"],
                  ["A344", "A133", "A378", "A157", "A149", "A183"], ["A348", "A136", "A096", "A091", "A305"]]]
    _, routing = build(places, crews=4, kits_per_truck=9)
    assert routing.ReadAssignmentFromRoutes(yesterday, True).ObjectiveValue() == 287
    tighter = [replace(s, window=(0, 300)) if s.name == "A305" else s for s in places]
    _, routing = build(tighter, crews=4, kits_per_truck=9)
    assert routing.ReadAssignmentFromRoutes(yesterday, True) is None


def test_too_few_kits_ends_without_routes():
    places = sites()
    manager, routing = build(places, crews=2, kits_per_truck=12)
    params = parameters()
    params.time_limit.FromSeconds(1)
    assert routing.SolveWithParameters(params) is None
    assert routing.status() in (routing_enums_pb2.RoutingSearchStatus.ROUTING_FAIL,
                                routing_enums_pb2.RoutingSearchStatus.ROUTING_FAIL_TIMEOUT,
                                routing_enums_pb2.RoutingSearchStatus.ROUTING_INFEASIBLE)
