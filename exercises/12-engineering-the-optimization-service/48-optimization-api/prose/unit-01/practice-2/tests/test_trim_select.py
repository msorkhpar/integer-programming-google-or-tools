import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")      # Starlette 1.10's notice that TestClient moves to httpx2
    from fastapi.testclient import TestClient

from trim_select import app

client = TestClient(app)

CIRCUITS = [
    {"circuit_id": "C-1", "cost": 400, "risk_reduction": 90.0},
    {"circuit_id": "C-2", "cost": 300, "risk_reduction": 85.0},
    {"circuit_id": "C-3", "cost": 300, "risk_reduction": 84.0},
    {"circuit_id": "C-4", "cost": 100, "risk_reduction": 10.0},
]


def post(budget, must_trim=(), circuits=CIRCUITS):
    return client.post("/selections", json={"budget": budget, "circuits": circuits, "must_trim": list(must_trim)})


def test_the_best_selection_within_the_budget():
    r = post(700)
    assert r.status_code == 200
    assert r.json() == {"status": "optimal", "chosen": ["C-2", "C-3", "C-4"], "cost": 700, "risk_reduction": 179.0}


def test_a_must_trim_circuit_is_always_chosen():
    body = post(700, must_trim=["C-1"]).json()
    assert body["status"] == "optimal"
    assert body["chosen"] == ["C-1", "C-2"] and body["cost"] == 700


def test_must_trims_over_budget_are_an_infeasible_answer_not_an_error():
    r = post(500, must_trim=["C-1", "C-2"])
    assert r.status_code == 200
    assert r.json() == {"status": "infeasible", "chosen": [], "cost": 0, "risk_reduction": 0.0}


def test_a_must_trim_naming_no_circuit_is_refused():
    assert post(700, must_trim=["C-9"]).status_code == 422
    assert post(700, must_trim=["C-4"]).status_code == 200


def test_a_circuit_listed_twice_is_refused():
    twice = CIRCUITS + [{"circuit_id": "C-4", "cost": 50, "risk_reduction": 30.0}]
    assert post(700, circuits=twice).status_code == 422
    assert post(700).status_code == 200
