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


def create_app(solve, db_path: str) -> FastAPI:
    app = FastAPI(title="Practice planning jobs")
    # TODO: the job table in the SQLite file at db_path, one worker thread, and the three endpoints.
    return app


if __name__ == "__main__":
    print(sorted(r.path for r in create_app(lambda budget: {"status": "optimal"}, ":memory:").routes))
