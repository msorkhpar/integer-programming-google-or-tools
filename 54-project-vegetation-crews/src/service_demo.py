"""Lesson 14.1.8: the planner as a service, called in-process through FastAPI's test client (the runner
has no network, so no server is started), with plans kept in a SQLite file."""

import json
import tempfile
import warnings
from pathlib import Path

from snapshots import use

use(8)
from vegcrew.api import create_app                 # noqa: E402
from vegcrew.generate import scenario              # noqa: E402

with warnings.catch_warnings():
    warnings.simplefilter("ignore")                # Starlette 1.10's notice about httpx (course finding F61)
    from fastapi.testclient import TestClient

with tempfile.TemporaryDirectory() as tmp:
    db = str(Path(tmp) / "plans.sqlite")
    api = TestClient(create_app(db))
    request = {"season": scenario("tiny"), "overrides": [{"kind": "skip", "cid": "C05", "reason": "flooded"}]}
    reply = api.post("/plans", json=request)
    body = reply.json()
    print(f"POST /plans -> {reply.status_code}, id {body['id']}, {body['record']['status']}, "
          f"risk carried ${body['record']['risk_carried']:,}k")
    print("  trims:", "; ".join(body["record"]["trims"]))
    again = TestClient(create_app(db)).get(f"/plans/{body['id']}")
    print(f"GET /plans/{body['id']} from a new app on the same file -> {again.status_code}, "
          f"same body: {again.json() == body}")
    print("GET /plans/7 ->", api.get("/plans/7").status_code, api.get("/plans/7").json())

    bad = {"season": scenario("tiny") | {"crews": 0}}
    reply = api.post("/plans", json=bad)
    detail = reply.json()["detail"][0]
    print(f"crews 0 -> {reply.status_code}: {detail['loc']} {detail['msg']}")
    request = {"season": scenario("tiny"), "overrides": [{"kind": "pin", "cid": "C01", "crew": "K3"}]}
    reply = api.post("/plans", json=request)
    print(f"pin on K3 -> {reply.status_code}: {json.dumps(reply.json())}")
    tight = scenario("tiny")
    for c in tight["circuits"]:
        c["must"] = True
    reply = api.post("/plans", json={"season": tight})
    record = reply.json()["record"]
    print(f"every circuit a must -> {reply.status_code}, {record['status']}:")
    for line in record["explanation"]:
        print("  -", line)
