"""Submit, poll, fetch: two jobs on lesson 12.4.2's job API, with one worker thread.

GridCap is fictional. Job A solves the medium portfolio with a 3-second limit; job B, the small one,
waits behind it. Output is collected and printed at the end, so nothing prints while HiGHS runs.
"""

import time
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi.testclient import TestClient  # noqa: E402

from job_api import create_app  # noqa: E402
from jobs import JobStore  # noqa: E402

store = JobStore()                 # a ThreadPoolExecutor with one worker
client = TestClient(create_app(store))
lines = []

a = client.post("/jobs", json={"portfolio": "medium", "time_limit_s": 3})
b = client.post("/jobs", json={"portfolio": "small"})
# Job A may still be "queued" for a moment, until the worker thread picks it up.
lines.append(f"POST medium -> {a.status_code} job_id {a.json()['job_id']}, poll {a.json()['poll']}")
lines.append(f"  Location: {a.headers['location']}")
lines.append(f"POST small  -> {b.status_code} {b.json()}")

while client.get("/jobs/job-1").json()["status"] == "queued":
    time.sleep(0.01)
lines.append(f"poll job-1 -> {client.get('/jobs/job-1').json()}")
lines.append(f"poll job-2 -> {client.get('/jobs/job-2').json()}")
early = client.get("/jobs/job-1/result")
lines.append(f"fetch job-1 now -> {early.status_code} {early.json()}")

slowest = 0.0
while not client.get("/jobs/job-2").json()["finished"]:
    start = time.perf_counter()
    client.get("/jobs/job-1")
    slowest = max(slowest, time.perf_counter() - start)
    time.sleep(0.05)
lines.append(f"every poll during the solves answered in under 0.1 s: {slowest < 0.1}")

for job_id in ("job-1", "job-2"):
    result = client.get(f"/jobs/{job_id}/result").json()
    lines.append(f"fetch {job_id} -> status {result['status']}, a plan: {bool(result['plan'])}, "
                 f"gap is {'zero' if result['gap'] == 0 else 'above zero'}")
missing = client.get("/jobs/job-9")
lines.append(f"poll job-9 -> {missing.status_code} {missing.json()}")
print("\n".join(lines))
