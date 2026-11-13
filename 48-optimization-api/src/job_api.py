"""Lesson 12.4.2's job API: submit returns a job id at once, poll returns a status, fetch returns the result.

GridCap is fictional. The solves run in the store's executor, never inside a request.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from jobs import FINISHED, Job, JobRequest, JobStore, Status
from schemas import PlanResult, to_result


class JobAccepted(BaseModel):
    job_id: str
    status: Status
    poll: str
    result: str


class JobStatus(BaseModel):
    job_id: str
    status: Status
    finished: bool


def create_app(store: JobStore) -> FastAPI:
    app = FastAPI(title="GridCap planning jobs", version="1.0.0")

    def find(job_id: str) -> Job:
        job = store.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"no job {job_id!r}")
        return job

    @app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
    def submit(request: JobRequest, response: Response) -> JobAccepted:
        job_id = store.submit(request)
        response.headers["Location"] = f"/jobs/{job_id}"
        return JobAccepted(job_id=job_id, status=store.status(find(job_id)),
                           poll=f"/jobs/{job_id}", result=f"/jobs/{job_id}/result")

    @app.get("/jobs/{job_id}", responses={404: {"description": "No job has that id"}})
    def poll(job_id: str) -> JobStatus:
        job = find(job_id)
        now = store.status(job)
        return JobStatus(job_id=job_id, status=now, finished=now in FINISHED)

    @app.get("/jobs/{job_id}/result",
             responses={404: {"description": "No job has that id"}, 409: {"description": "The job has not finished"}})
    def fetch(job_id: str) -> PlanResult:
        job = find(job_id)
        if not job.future.done():
            raise HTTPException(status_code=409, detail=f"job {job_id} is {store.status(job)}; poll /jobs/{job_id}")
        return to_result(job_id, job.request, store.outcome(job))

    return app
