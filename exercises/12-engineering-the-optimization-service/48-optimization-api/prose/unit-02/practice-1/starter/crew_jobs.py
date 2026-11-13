from __future__ import annotations

import threading
import uuid  # noqa: F401
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
        # TODO: mark the job running, solve, and record the result, or the failure and its reason.
        pass

    def find(job_id: str) -> Job:
        with lock:
            job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"no job {job_id}")
        return job

    # TODO: submit must answer 202 at once and leave the solve to the pool; fetch must answer 409 early.
    @app.post("/jobs")
    def submit(request: RosterRequest) -> dict:
        return {"job_id": "", "status": "queued"}

    @app.get("/jobs/{job_id}")
    def poll(job_id: str) -> dict:
        return {"job_id": job_id, "status": "queued", "message": "", "ahead": 0}

    @app.get("/jobs/{job_id}/result")
    def fetch(job_id: str) -> dict:
        return {}

    return app


if __name__ == "__main__":
    app = create_app(lambda request: {"status": "optimal", "crews_used": request.crews})
    print(sorted(app.openapi()["paths"]))
