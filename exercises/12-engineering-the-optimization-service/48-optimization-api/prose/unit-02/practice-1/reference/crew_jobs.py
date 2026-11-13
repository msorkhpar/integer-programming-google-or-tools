from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


class RosterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    crews: int = Field(ge=1)
    weeks: int = Field(ge=1, le=52)


@dataclass
class Job:
    status: str = "queued"           # queued -> running -> the solve's own status, or failed
    result: dict | None = None
    message: str = ""


def create_app(solve: Callable[[RosterRequest], dict], workers: int = 1) -> FastAPI:
    """A job API around `solve`, which takes minutes and returns a dict with a "status" key."""
    app = FastAPI(title="Crew roster jobs")
    jobs: dict[str, Job] = {}
    order: list[str] = []            # job ids in the order they were submitted
    lock = threading.Lock()
    pool = ThreadPoolExecutor(max_workers=workers)

    def work(job_id: str, request: RosterRequest) -> None:
        with lock:
            jobs[job_id].status = "running"
        try:
            result = solve(request)
        except Exception as error:
            with lock:
                jobs[job_id].status, jobs[job_id].message = "failed", f"the solve failed: {error}"
            return
        with lock:
            jobs[job_id].status, jobs[job_id].result = result["status"], result

    def find(job_id: str) -> Job:
        with lock:
            job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"no job {job_id}")
        return job

    @app.post("/jobs", status_code=202)
    def submit(request: RosterRequest) -> dict:
        job_id = uuid.uuid4().hex
        with lock:
            jobs[job_id] = Job()
            order.append(job_id)
        pool.submit(work, job_id, request)
        return {"job_id": job_id, "status": "queued"}

    @app.get("/jobs/{job_id}")
    def poll(job_id: str) -> dict:
        job = find(job_id)
        with lock:
            earlier = order[:order.index(job_id)]
            ahead = sum(1 for other in earlier if jobs[other].status == "queued") if job.status == "queued" else 0
        return {"job_id": job_id, "status": job.status, "message": job.message, "ahead": ahead}

    @app.get("/jobs/{job_id}/result")
    def fetch(job_id: str) -> dict:
        job = find(job_id)
        if job.status in ("queued", "running"):
            raise HTTPException(status_code=409, detail=f"job {job_id} is {job.status}")
        return job.result if job.result is not None else {"status": job.status, "message": job.message}

    return app


if __name__ == "__main__":
    app = create_app(lambda request: {"status": "optimal", "crews_used": request.crews})
    print(sorted(app.openapi()["paths"]))
