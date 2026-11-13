import threading
import time
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")      # Starlette 1.10's notice that TestClient moves to httpx2
    from fastapi.testclient import TestClient

from crew_jobs import create_app

ROSTER = {"crews": 4, "weeks": 6}


def quick(request):
    if request.crews == 13:
        raise RuntimeError("crew calendar for crew 13 is missing")
    return {"status": "optimal", "crews_used": request.crews, "weeks": request.weeks}


def client_for(solve):
    return TestClient(create_app(solve), raise_server_exceptions=False)


def wait_until(client, job_id, done, seconds=3.0):
    """Poll until done(status) holds or the time runs out; return the last poll's body."""
    deadline = time.monotonic() + seconds
    body = client.get(f"/jobs/{job_id}").json()
    while not done(body.get("status")) and time.monotonic() < deadline:
        time.sleep(0.01)
        body = client.get(f"/jobs/{job_id}").json()
    return body


def held_solver():
    release = threading.Event()

    def solve(request):
        release.wait(5)
        return quick(request)
    return solve, release


def test_submit_poll_and_fetch_a_finished_job():
    client = client_for(quick)
    accepted = client.post("/jobs", json=ROSTER)
    assert accepted.status_code == 202
    job_id = accepted.json().get("job_id")
    assert wait_until(client, job_id, lambda s: s == "optimal").get("status") == "optimal"
    fetched = client.get(f"/jobs/{job_id}/result")
    assert fetched.status_code == 200
    assert fetched.json() == {"status": "optimal", "crews_used": 4, "weeks": 6}


def test_submit_answers_before_the_solve_finishes():
    solve, release = held_solver()
    client = client_for(solve)
    start = time.monotonic()
    accepted = client.post("/jobs", json=ROSTER)
    took = time.monotonic() - start
    release.set()
    assert accepted.status_code == 202 and took < 1.0


def test_a_second_job_waits_in_the_queue():
    solve, release = held_solver()
    client = client_for(solve)
    first = client.post("/jobs", json=ROSTER).json().get("job_id")
    second = client.post("/jobs", json=ROSTER).json().get("job_id")
    running = wait_until(client, first, lambda s: s == "running").get("status")
    waiting = client.get(f"/jobs/{second}").json().get("status")
    release.set()
    assert (running, waiting) == ("running", "queued")


def test_an_unknown_job_is_404():
    client = client_for(quick)
    job_id = client.post("/jobs", json=ROSTER).json().get("job_id")
    assert client.get(f"/jobs/{job_id}x").status_code == 404
    assert client.get(f"/jobs/{job_id}x/result").status_code == 404


def test_fetching_before_the_end_is_409():
    solve, release = held_solver()
    client = client_for(solve)
    job_id = client.post("/jobs", json=ROSTER).json().get("job_id")
    early = client.get(f"/jobs/{job_id}/result").status_code
    release.set()
    wait_until(client, job_id, lambda s: s == "optimal")
    assert (early, client.get(f"/jobs/{job_id}/result").status_code) == (409, 200)


def test_a_solve_that_raises_ends_failed_and_the_next_job_still_runs():
    client = client_for(quick)
    bad = client.post("/jobs", json={"crews": 13, "weeks": 6}).json().get("job_id")
    body = wait_until(client, bad, lambda s: s == "failed")
    assert body.get("status") == "failed" and "crew 13" in body.get("message", "")
    good = client.post("/jobs", json=ROSTER).json().get("job_id")
    assert wait_until(client, good, lambda s: s == "optimal").get("status") == "optimal"


def test_a_queued_job_says_how_many_jobs_wait_ahead_of_it():
    solve, release = held_solver()
    client = client_for(solve)
    ids = [client.post("/jobs", json=ROSTER).json().get("job_id") for _ in range(3)]
    wait_until(client, ids[0], lambda s: s == "running")
    ahead = [client.get(f"/jobs/{job_id}").json().get("ahead") for job_id in ids]
    release.set()
    assert ahead == [0, 0, 1]
