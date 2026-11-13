"""FastAPI's BackgroundTasks as a job runner: what a TestClient sees, and what it cannot tell you.

`time.sleep(1)` stands in for a one-second solve.
"""

import time
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi import BackgroundTasks, FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

app = FastAPI()
jobs: dict[str, str] = {}


def solve(job_id: str) -> None:
    jobs[job_id] = "running"
    time.sleep(1)
    jobs[job_id] = "optimal"


@app.post("/jobs", status_code=202)
def submit(background: BackgroundTasks) -> dict:
    job_id = f"job-{len(jobs) + 1}"
    jobs[job_id] = "queued"
    background.add_task(solve, job_id)
    return {"job_id": job_id, "status": jobs[job_id]}


@app.get("/jobs/{job_id}")
def poll(job_id: str) -> dict:
    return {"job_id": job_id, "status": jobs[job_id]}


client = TestClient(app)
start = time.perf_counter()
accepted = client.post("/jobs")
took = time.perf_counter() - start
print(f"POST /jobs -> {accepted.status_code} {accepted.json()} after {took:.0f} s")
print("first poll ->", client.get(f"/jobs/{accepted.json()['job_id']}").json())
