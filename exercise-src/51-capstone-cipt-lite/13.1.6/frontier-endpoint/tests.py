import itertools
import json
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")    # Starlette 1.10's notice about httpx2
from fastapi.testclient import TestClient                    # noqa: E402

from frontier_endpoint import best, check, create_app, frontier, starts   # noqa: E402


def job(cost, earliest, latest, npv, risk, group=None):
    years = range(earliest, latest + 1)
    return {"cost": cost, "earliest": earliest, "latest": latest, "must": False, "parent": None, "lag": 0,
            "group": group, "npv": dict(zip(years, npv)), "risk": dict(zip(years, risk))}


SNAPSHOT = {"years": [2027, 2028], "budget": {2027: 200, 2028: 200}, "projects": {
    "J1": job([100], 2027, 2028, [50, 50], [10, 8]),
    "J2": job([100], 2027, 2028, [40, 38], [30, 25]),
    "J3": job([100], 2027, 2027, [60], [5]),
    "J4": job([100], 2028, 2028, [30], [40]),
    "J5": job([100], 2027, 2028, [45, 45], [35, 50], group="G1"),
    "J6": job([100], 2027, 2028, [20, 18], [60, 55], group="G1"),
}}


def every_plan(snapshot):
    jobs = snapshot["projects"]
    options = [[None, *starts(jobs[j])] for j in sorted(jobs)]
    for choice in itertools.product(*options):
        plan = {j: t for j, t in zip(sorted(jobs), choice) if t is not None}
        if not check(snapshot, plan):
            yield (sum(jobs[j]["npv"][t] for j, t in plan.items()), sum(jobs[j]["risk"][t] for j, t in plan.items()))


VALUES = set(every_plan(SNAPSHOT))
PARETO = {p for p in VALUES if not any(q[0] >= p[0] and q[1] >= p[1] and q != p for q in VALUES)}
TOP_NPV = max(VALUES)                                         # most NPV, then most risk
TOP_RISK = max(VALUES, key=lambda v: (v[1], v[0]))            # most risk, then most NPV


def pairs(points):
    return [(p.get("npv"), p.get("risk")) for p in points]


def as_json(snapshot):
    return json.loads(json.dumps(snapshot))                   # year keys become text, as over HTTP


def test_the_endpoint_returns_pareto_points_from_end_to_end():
    client = TestClient(create_app(), raise_server_exceptions=False)
    r = client.post("/frontier", json={"snapshot": as_json(SNAPSHOT), "points": 5})
    assert r.status_code == 200
    got = pairs(r.json().get("points", []))
    assert got and set(got) <= PARETO
    assert got[0] == TOP_NPV and got[-1] == TOP_RISK and got == sorted(got, key=lambda v: v[1])
    for n in (1, 12):
        assert client.post("/frontier", json={"snapshot": as_json(SNAPSHOT), "points": n}).status_code == 422


# One year, room for one project: A and B tie on NPV, C and D tie on risk removed.
TIES = {"years": [2027], "budget": {2027: 100}, "projects": {
    "A": job([100], 2027, 2027, [50], [10]), "B": job([100], 2027, 2027, [50], [30]),
    "C": job([100], 2027, 2027, [20], [70]), "D": job([100], 2027, 2027, [25], [70])}}


def test_each_end_is_lexicographic_so_no_end_is_weakly_dominated():
    top_npv = best(TIES, "npv", "risk", {}) or {}
    top_risk = best(TIES, "risk", "npv", {}) or {}
    assert (top_npv.get("npv"), top_npv.get("risk")) == (50, 30)
    assert (top_risk.get("npv"), top_risk.get("risk")) == (25, 70)


def test_no_point_is_repeated_or_dominated_when_floors_share_a_plan():
    got = pairs(frontier(SNAPSHOT, 11))
    assert got and len(got) == len(set(got)) and set(got) <= PARETO


def test_two_points_are_the_two_ends():
    assert pairs(frontier(SNAPSHOT, 2)) == [TOP_NPV, TOP_RISK]


# Risk tables are rounded to $0.001k, so an optimum can be fractional. Room for one project:
# C and D remove the most risk, 70.4; E removes a little less and is worth more.
FRACTIONAL = {"years": [2027], "budget": {2027: 100}, "projects": {
    "A": job([100], 2027, 2027, [50], [10.2]), "C": job([100], 2027, 2027, [20], [70.4]),
    "D": job([100], 2027, 2027, [25], [70.4]), "E": job([100], 2027, 2027, [40], [70.1])}}


def test_the_hold_row_keeps_a_fractional_optimum():
    top_risk = best(FRACTIONAL, "risk", "npv", {}) or {}
    assert top_risk.get("npv") == 25 and abs(top_risk.get("risk", 0) - 70.4) < 1e-9
