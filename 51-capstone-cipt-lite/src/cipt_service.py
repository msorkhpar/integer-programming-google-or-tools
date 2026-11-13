"""CIPT Lite, milestone 6: the service. Snapshots and results in S3, job states in a local SQLite file.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

* `S3Store` keeps each snapshot once under `snapshots/<digest>.json` and re-hashes it on every
  read (lesson 12.2.3), and each job's result under `results/<job id>.json`. Its tests run against
  moto's in-memory S3, with moto's fake credentials and no network.
* `JobTable` is the job log in a local SQLite file: one row per job, its state, and the snapshot it
  solves (lesson 12.1.4). SQLite only, as in lesson 12.5.3: no cloud database.
* `create_app(store, table)` is the FastAPI app (lessons 12.4.1-12.4.3): POST a snapshot, POST a
  job and get 202 with its id, poll it, fetch its result, or 409 before it exists; POST a frontier
  request and get NPV against risk removed, every point checked as non-dominated (lesson 8.3.3).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from concurrent.futures import Executor, ThreadPoolExecutor
from pathlib import Path

from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, Response, status
from ortools.math_opt.python import mathopt
from pydantic import BaseModel, ConfigDict, Field

from cipt_data import Finding, canonical, gate
from cipt_model import Scenario, build, check, params, plan_of, solve
from cipt_value import risk_table
from gridcap import Portfolio


class Corrupted(Exception):
    pass


class S3Store:
    def __init__(self, client, bucket: str):
        self.s3, self.bucket = client, bucket

    def put_snapshot(self, pf: Portfolio) -> str:
        data = canonical(pf)
        key = hashlib.sha256(data).hexdigest()
        if not self.exists(f"snapshots/{key}.json"):
            self.s3.put_object(Bucket=self.bucket, Key=f"snapshots/{key}.json", Body=data,
                               ContentType="application/json")
        return key

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as error:
            if error.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise

    def get_snapshot(self, digest: str) -> Portfolio:
        data = self.s3.get_object(Bucket=self.bucket, Key=f"snapshots/{digest}.json")["Body"].read()
        if hashlib.sha256(data).hexdigest() != digest:
            raise Corrupted(f"snapshots/{digest[:12]}.json no longer hashes to its name")
        return Portfolio.from_dict(json.loads(data))

    def put_result(self, job_id: str, result: dict) -> None:
        self.s3.put_object(Bucket=self.bucket, Key=f"results/{job_id}.json",
                           Body=json.dumps(result, sort_keys=True).encode("utf-8"), ContentType="application/json")

    def get_result(self, job_id: str) -> dict:
        return json.loads(self.s3.get_object(Bucket=self.bucket, Key=f"results/{job_id}.json")["Body"].read())


class JobTable:
    """Jobs in a local SQLite file. One connection, used under a lock by the API and the worker."""

    def __init__(self, path: str | Path):
        self.db = sqlite3.connect(path, check_same_thread=False, autocommit=True)
        self.lock = threading.Lock()
        self.db.execute("CREATE TABLE IF NOT EXISTS job (id TEXT PRIMARY KEY, snapshot TEXT NOT NULL, "
                        "request TEXT NOT NULL, state TEXT NOT NULL) STRICT")

    def add(self, job_id: str, snapshot: str, request: str) -> None:
        with self.lock:
            self.db.execute("INSERT INTO job VALUES (?, ?, ?, 'queued')", (job_id, snapshot, request))

    def set_state(self, job_id: str, state: str) -> None:
        with self.lock:
            self.db.execute("UPDATE job SET state = ? WHERE id = ?", (state, job_id))

    def state(self, job_id: str) -> str | None:
        with self.lock:
            row = self.db.execute("SELECT state FROM job WHERE id = ?", (job_id,)).fetchone()
        return row[0] if row else None


FINISHED = ("optimal", "feasible", "infeasible", "failed")


class JobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot: str = Field(pattern=r"^[0-9a-f]{64}$")
    budget: dict[int, int] = Field(default_factory=dict)
    gap: float = Field(default=1e-3, ge=0.0, le=0.1)


class FrontierRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot: str = Field(pattern=r"^[0-9a-f]{64}$")
    points: int = Field(default=5, ge=2, le=11)
    gap: float = Field(default=1e-3, ge=0.0, le=0.1)


def run_job(store: S3Store, pf: Portfolio, request: JobRequest) -> dict:
    sc = Scenario(name="request", budget=dict(request.budget))
    b = build(pf, sc)
    result = solve(b.model, params(gap=request.gap))
    reason = result.termination.reason
    if reason == mathopt.TerminationReason.INFEASIBLE:
        return {"status": "infeasible", "npv": None, "bound": None, "starts": {}}
    if not result.has_primal_feasible_solution():
        return {"status": "failed", "npv": None, "bound": None, "starts": {}}
    plan = plan_of(b, result)
    assert not check(pf, sc, plan), "the solver's plan breaks a rule"
    return {"status": "optimal" if reason == mathopt.TerminationReason.OPTIMAL else "feasible",
            "npv": round(result.objective_value(), 3), "bound": round(result.termination.objective_bounds.dual_bound, 3),
            "starts": plan}


def frontier(pf: Portfolio, points: int, gap: float) -> list[dict]:
    """NPV against risk removed by the epsilon-constraint method (lesson 8.3.1), dominated points dropped."""
    rr = risk_table(pf)
    b = build(pf)
    risk = mathopt.fast_sum(rr[k] * x for k, x in b.x.items())

    def best(floor: float | None) -> dict | None:
        row = b.model.add_linear_constraint(risk >= floor, name="floor") if floor is not None else None
        result = solve(b.model, params(gap=gap))
        if row is not None:
            b.model.delete_linear_constraint(row)
        if not result.has_primal_feasible_solution():
            return None
        plan = plan_of(b, result)
        return {"npv": sum(pf.project(i).npv[t] for i, t in plan.items()),
                "risk": round(sum(rr[i, t] for i, t in plan.items()), 1), "projects": len(plan)}

    b.model.maximize(risk)
    most = best(None)
    b.model.maximize(b.npv)
    low = best(None)["risk"]
    found = []
    for k in range(points):
        p = best(low + (most["risk"] - low) * k / (points - 1))
        if p is not None:
            found.append(p)
    return [p for p in found
            if not any(q["npv"] >= p["npv"] and q["risk"] >= p["risk"] and q != p for q in found)]


def create_app(store: S3Store, table: JobTable, executor: Executor | None = None) -> FastAPI:
    app = FastAPI(title="CIPT Lite", version="1.0.0")
    pool = executor or ThreadPoolExecutor(max_workers=1)

    def snapshot_of(digest: str) -> Portfolio:
        if not store.exists(f"snapshots/{digest}.json"):
            raise HTTPException(status_code=404, detail=f"no snapshot {digest[:12]}")
        return store.get_snapshot(digest)

    @app.post("/snapshots", status_code=status.HTTP_201_CREATED)
    def put_snapshot(portfolio: dict) -> dict:
        try:
            pf = Portfolio.from_dict(portfolio)
        except (KeyError, TypeError, ValueError) as error:
            raise HTTPException(status_code=422, detail=f"not a portfolio: {error!r}")
        findings: list[Finding] = gate(pf)
        errors = [f"{f.rule}: {f.subject}" for f in findings if f.severity == "error"]
        if errors:
            raise HTTPException(status_code=422, detail=errors)
        return {"snapshot": store.put_snapshot(pf), "warnings": [f.rule for f in findings]}

    def work(job_id: str, pf: Portfolio, request: JobRequest) -> None:
        table.set_state(job_id, "running")
        try:
            outcome = run_job(store, pf, request)
        except Exception as error:                       # a job fails; the service stays up
            outcome = {"status": "failed", "npv": None, "bound": None, "starts": {}, "error": type(error).__name__}
        store.put_result(job_id, {"job_id": job_id, "snapshot": request.snapshot, **outcome})
        table.set_state(job_id, outcome["status"])

    @app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
    def submit(request: JobRequest, response: Response) -> dict:
        pf = snapshot_of(request.snapshot)
        unknown = sorted(set(request.budget) - set(pf.years))
        if unknown:
            raise HTTPException(status_code=422, detail=f"years outside the plan: {unknown}")
        job_id = uuid.uuid4().hex[:12]
        table.add(job_id, request.snapshot, request.model_dump_json())
        pool.submit(work, job_id, pf, request)
        response.headers["Location"] = f"/jobs/{job_id}"
        return {"job_id": job_id, "poll": f"/jobs/{job_id}", "result": f"/jobs/{job_id}/result"}

    @app.get("/jobs/{job_id}")
    def poll(job_id: str) -> dict:
        state = table.state(job_id)
        if state is None:
            raise HTTPException(status_code=404, detail=f"no job {job_id!r}")
        return {"job_id": job_id, "state": state, "finished": state in FINISHED}

    @app.get("/jobs/{job_id}/result")
    def fetch(job_id: str) -> dict:
        state = poll(job_id)["state"]
        if state not in FINISHED:
            raise HTTPException(status_code=409, detail=f"job {job_id} is {state}")
        return store.get_result(job_id)

    @app.post("/frontier")
    def pareto(request: FrontierRequest) -> dict:
        return {"snapshot": request.snapshot, "objectives": ["npv", "risk"],
                "points": frontier(snapshot_of(request.snapshot), request.points, request.gap)}

    return app
