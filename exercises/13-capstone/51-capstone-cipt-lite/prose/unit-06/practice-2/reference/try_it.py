"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import os
import tempfile
import time
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")
from fastapi.testclient import TestClient  # noqa: E402

from job_api import create_app  # noqa: E402


def solve(budget):
    """A stand-in planning run: no plan below $200k in any year."""
    if budget.get(2032) == 7:
        raise ValueError("no prices for 2032")
    if any(amount < 200 for amount in budget.values()):
        return {"status": "infeasible", "npv": None}
    return {"status": "optimal", "npv": 410, "starts": {"P2": 2031}}


def finish(client, job_id):
    for _ in range(300):
        body = client.get(f"/jobs/{job_id}").json()
        if body.get("finished"):
            break
        time.sleep(0.01)
    return client.get(f"/jobs/{job_id}/result").json()


with tempfile.TemporaryDirectory() as folder:
    client = TestClient(create_app(solve, os.path.join(folder, "jobs.sqlite")))
    for budget in ({"2031": 250}, {"2031": 150}, {"2032": 7}):
        reply = client.post("/jobs", json={"budget": budget})
        print(f"budget {budget}:", reply.status_code, finish(client, reply.json().get("job_id")))
    print("poll of job 'unknown':", client.get("/jobs/unknown").status_code)
