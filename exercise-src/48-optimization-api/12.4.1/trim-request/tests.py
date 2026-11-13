import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")      # Starlette 1.10's notice that TestClient moves to httpx2
    from fastapi.testclient import TestClient

from trim_api import app

client = TestClient(app)


def request(budget=900, circuits=None, **extra):
    if circuits is None:
        circuits = [{"circuit_id": "C-14", "miles": 12.5, "cost": 300},
                    {"circuit_id": "C-22", "miles": 4.0, "cost": 120}]
    return {"budget": budget, "circuits": circuits, **extra}


def status(body):
    return client.post("/trims", json=body).status_code


def circuit(cid="C-30", miles=3.0, cost=80):
    return {"circuit_id": cid, "miles": miles, "cost": cost}


def test_a_valid_request_is_accepted_and_a_negative_budget_refused():
    assert status(request()) == 200
    assert status(request(budget=-1)) == 422


def test_a_zero_budget_is_accepted_and_a_negative_cost_refused():
    assert status(request(budget=0)) == 200
    assert status(request(circuits=[circuit(cost=-5)])) == 422


def test_a_circuit_with_no_miles_is_refused():
    assert status(request(circuits=[circuit(miles=0.5)])) == 200
    assert status(request(circuits=[circuit(miles=0)])) == 422


def test_repeated_circuit_ids_are_refused():
    assert status(request(circuits=[circuit("C-30"), circuit("C-31")])) == 200
    assert status(request(circuits=[circuit("C-30"), circuit("C-30")])) == 422


def test_an_empty_circuit_list_is_refused():
    assert status(request(circuits=[circuit()])) == 200
    assert status(request(circuits=[])) == 422


def test_a_misspelled_field_is_refused():
    assert status(request()) == 200
    assert status(request(budjet=900)) == 422


def test_a_misspelled_circuit_field_is_refused():
    assert status(request(circuits=[circuit()])) == 200
    assert status(request(circuits=[{**circuit(), "mile": 3.0}])) == 422


def test_an_empty_circuit_id_is_refused():
    assert status(request(circuits=[circuit("X")])) == 200
    assert status(request(circuits=[circuit("")])) == 422
