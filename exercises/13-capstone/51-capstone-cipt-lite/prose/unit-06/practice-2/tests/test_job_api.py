import sqlite3
import threading
import time
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")    # Starlette 1.10's notice about httpx2
from fastapi.testclient import TestClient                    # noqa: E402

from job_api import create_app                               # noqa: E402

PLAN = {"status": "optimal", "npv": 230, "starts": {"J1": 2027, "J3": 2028}}


def solve(budget):
    """A stand-in planning run: infeasible below $100k in any year, the same plan otherwise."""
    assert all(isinstance(year, int) for year in budget), "years must reach the solve as integers"
    if budget.get(2029) == 13:
        raise RuntimeError("no crew calendar for 2029")
    if any(amount < 100 for amount in budget.values()):
        return {"status": "infeasible", "npv": None, "starts": {}}
    return PLAN


def wait(client, job_id, seconds=3.0):
    deadline = time.monotonic() + seconds
    body = client.get(f"/jobs/{job_id}").json()
    while not body.get("finished") and time.monotonic() < deadline:
        time.sleep(0.01)
        body = client.get(f"/jobs/{job_id}").json()
    return body


def test_submit_poll_and_fetch(tmp_path):
    client = TestClient(create_app(solve, str(tmp_path / "jobs.sqlite")))
    r = client.post("/jobs", json={"budget": {"2028": 300}})
    assert r.status_code == 202
    job_id = r.json().get("job_id")
    assert job_id and r.headers.get("location") == f"/jobs/{job_id}"
    assert r.json().get("poll") == f"/jobs/{job_id}" and r.json().get("result") == f"/jobs/{job_id}/result"
    assert wait(client, job_id).get("state") == "optimal"
    got = client.get(f"/jobs/{job_id}/result")
    assert got.status_code == 200 and got.json() == PLAN
    r = client.post("/jobs", json={"budget": {"2028": 50}})
    assert wait(client, r.json()["job_id"]).get("state") == "infeasible"


def test_an_unknown_job_is_404(tmp_path):
    client = TestClient(create_app(solve, str(tmp_path / "jobs.sqlite")))
    for path in ("/jobs/nope", "/jobs/nope/result"):
        r = client.get(path)
        assert r.status_code == 404 and "nope" in str(r.json().get("detail")), "say which id is unknown"


def test_fetching_before_the_job_finishes_is_409(tmp_path):
    gate = threading.Event()

    def slow(budget):
        gate.wait(3)
        return PLAN

    client = TestClient(create_app(slow, str(tmp_path / "jobs.sqlite")))
    job_id = client.post("/jobs", json={}).json().get("job_id")
    early = client.get(f"/jobs/{job_id}/result").status_code
    gate.set()
    wait(client, job_id)
    assert early == 409 and client.get(f"/jobs/{job_id}/result").status_code == 200


def test_a_finished_job_survives_a_restart(tmp_path):
    path = str(tmp_path / "jobs.sqlite")
    first = TestClient(create_app(solve, path))
    job_id = first.post("/jobs", json={}).json().get("job_id")
    wait(first, job_id)
    second = TestClient(create_app(solve, path))           # a new process of the service, same file
    assert second.get(f"/jobs/{job_id}").json().get("state") == "optimal"
    assert second.get(f"/jobs/{job_id}/result").json() == PLAN
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT state FROM job WHERE id = ?", (job_id,)).fetchone() == ("optimal",)


def test_a_solve_that_raises_fails_its_job_and_the_next_job_runs(tmp_path):
    client = TestClient(create_app(solve, str(tmp_path / "jobs.sqlite")))
    bad = client.post("/jobs", json={"budget": {"2029": 13}}).json().get("job_id")
    assert wait(client, bad).get("state") == "failed"
    assert "crew calendar" in client.get(f"/jobs/{bad}/result").json().get("error", "")
    good = client.post("/jobs", json={}).json().get("job_id")
    assert wait(client, good).get("state") == "optimal"


def test_a_request_with_an_unknown_field_is_422(tmp_path):
    client = TestClient(create_app(solve, str(tmp_path / "jobs.sqlite")))
    assert client.post("/jobs", json={"budgets": {"2028": 300}}).status_code == 422
