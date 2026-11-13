"""Milestone 6: the planning job API, with every job's state and result in a local SQLite file.

`create_app(solve, db_path)` builds the app. `solve(budget)` is the planning run (milestone 2's model
behind it in the service); it takes {year: $k} overrides and returns a JSON-ready result dict with a
"status". Jobs run on one worker thread; their state survives a restart because it is in the file.
The practice portfolio behind the solves is invented for a fictional utility.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

FINISHED = ("optimal", "infeasible", "failed")


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    budget: dict[int, int] = Field(default_factory=dict)


class Jobs:
    """The job table in a SQLite file, one connection shared under a lock."""

    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False, autocommit=True)
        self.lock = threading.Lock()
        self.db.execute("CREATE TABLE IF NOT EXISTS job (id TEXT PRIMARY KEY, request TEXT NOT NULL, "
                        "state TEXT NOT NULL, result TEXT) STRICT")

    def add(self, job_id: str, request: str) -> None:
        with self.lock:
            self.db.execute("INSERT INTO job (id, request, state) VALUES (?, ?, 'queued')", (job_id, request))

    def finish(self, job_id: str, state: str, result: dict | None = None) -> None:
        with self.lock:
            self.db.execute("UPDATE job SET state = ?, result = ? WHERE id = ?",
                            (state, None if result is None else json.dumps(result), job_id))

    def row(self, job_id: str) -> tuple[str, str | None] | None:
        with self.lock:
            return self.db.execute("SELECT state, result FROM job WHERE id = ?", (job_id,)).fetchone()


def create_app(solve, db_path: str) -> FastAPI:
    app = FastAPI(title="Practice planning jobs")
    jobs = Jobs(db_path)
    pool = ThreadPoolExecutor(max_workers=1)

    def work(job_id: str, request: PlanRequest) -> None:
        jobs.finish(job_id, "running")
        try:
            result = solve(dict(request.budget))
            jobs.finish(job_id, result["status"], result)
        except Exception as error:                     # one job fails; the service goes on
            jobs.finish(job_id, "failed", {"status": "failed", "error": f"{type(error).__name__}: {error}"})

    @app.post("/jobs", status_code=202)
    def submit(request: PlanRequest, response: Response) -> dict:
        job_id = uuid.uuid4().hex
        jobs.add(job_id, request.model_dump_json())
        pool.submit(work, job_id, request)
        response.headers["Location"] = f"/jobs/{job_id}"
        return {"job_id": job_id, "poll": f"/jobs/{job_id}", "result": f"/jobs/{job_id}/result"}

    @app.get("/jobs/{job_id}")
    def poll(job_id: str) -> dict:
        row = jobs.row(job_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"no job {job_id}")
        return {"job_id": job_id, "state": row[0], "finished": row[0] in FINISHED}

    @app.get("/jobs/{job_id}/result")
    def fetch(job_id: str) -> dict:
        state = poll(job_id)["state"]
        if state not in FINISHED:
            raise HTTPException(status_code=409, detail=f"job {job_id} is {state}")
        return json.loads(jobs.row(job_id)[1])

    return app


if __name__ == "__main__":
    print(sorted(r.path for r in create_app(lambda budget: {"status": "optimal"}, ":memory:").routes))
