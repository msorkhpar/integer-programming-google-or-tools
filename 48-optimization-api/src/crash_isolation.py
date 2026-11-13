"""A solve that kills its process: in a worker process, the job fails and the API keeps answering.

GridCap is fictional. The worker processes come from a ProcessPoolExecutor; the API, its job store
and the TestClient stay in this process. Each worker process imports this file again, so its top
level imports nothing but the standard library: a worker loads only what its job's function needs.
"""

import warnings
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool


def main() -> None:
    warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
    from fastapi.testclient import TestClient

    from job_api import create_app
    from jobs import JobStore, run_job
    from legacy_report import run_job_with_pulp_report

    store = JobStore(ProcessPoolExecutor(max_workers=1), worker=run_job_with_pulp_report)
    client = TestClient(create_app(store))

    job_id = client.post("/jobs", json={"portfolio": "small"}).json()["job_id"]
    store.get(job_id).future.exception()          # wait for the worker to finish, or to die
    print("poll  ->", client.get(f"/jobs/{job_id}").json())
    print("fetch ->", client.get(f"/jobs/{job_id}/result").json()["message"])
    print("the API still answers: GET /jobs/job-1 ->", client.get(f"/jobs/{job_id}").status_code)

    try:
        store.executor.submit(run_job, None).result()
    except BrokenProcessPool:
        print("the old pool takes no more work: BrokenProcessPool")
    store.executor, store.worker = ProcessPoolExecutor(max_workers=1), run_job
    job_id = client.post("/jobs", json={"portfolio": "small"}).json()["job_id"]
    store.get(job_id).future.result()
    print("new pool, next job ->", client.get(f"/jobs/{job_id}").json())


if __name__ == "__main__":      # worker processes import this file too; only the parent runs main()
    main()
