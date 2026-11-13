"""From script to service: the HTTP API and its SQLite store (lesson 14.1.8)."""

import warnings

from vegcrew.api import create_app
from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
from vegcrew.record import plan_record

with warnings.catch_warnings():
    warnings.simplefilter("ignore")              # Starlette 1.10's deprecation notice about httpx
    from fastapi.testclient import TestClient


def client(db=":memory:"):
    return TestClient(create_app(db))


def tiny_request(**changes):
    return {"season": scenario("tiny") | changes, "overrides": []}


def test_posting_a_season_returns_the_record_the_library_gives():
    raw = scenario("tiny")
    reply = client().post("/plans", json=tiny_request())
    assert reply.status_code == 200
    expected = plan_record(raw, make_plan(season_from_dict(raw)))
    assert reply.json()["record"]["trims"] == expected["trims"]
    assert reply.json()["record"]["risk_carried"] == expected["risk_carried"]


def test_a_stored_plan_comes_back_by_its_id_and_an_unknown_id_is_404():
    api = client()
    reply = api.post("/plans", json=tiny_request())
    assert reply.status_code == 200
    posted = reply.json()
    assert api.get(f"/plans/{posted['id']}").json() == posted
    missing = api.get("/plans/99")
    assert (missing.status_code, missing.json()) == (404, {"detail": "no plan 99"})


def test_a_season_that_breaks_the_schema_is_refused_with_422():
    reply = client().post("/plans", json=tiny_request(budget=-5))
    assert reply.status_code == 422
    assert reply.json()["detail"][0]["loc"] == ["body", "season", "budget"]


def test_an_override_that_names_no_circuit_is_refused_with_its_problem():
    request = tiny_request()
    request["overrides"] = [{"kind": "skip", "cid": "Z9"}]
    reply = client().post("/plans", json=request)
    assert (reply.status_code, reply.json()) == (422, {"detail": ["override 1: no circuit Z9"]})


def test_an_infeasible_season_is_an_answer_with_its_explanation():
    raw = scenario("tiny")
    for c in raw["circuits"]:
        c["must"] = True
    reply = client().post("/plans", json={"season": raw})
    assert reply.status_code == 200
    assert reply.json()["record"]["status"] == "INFEASIBLE"
    assert reply.json()["record"]["explanation"]


def test_plans_outlive_the_service_in_the_sqlite_file(tmp_path):
    db = str(tmp_path / "plans.sqlite")
    reply = client(db).post("/plans", json=tiny_request())
    assert reply.status_code == 200
    assert client(db).get(f"/plans/{reply.json()['id']}").json() == reply.json()
