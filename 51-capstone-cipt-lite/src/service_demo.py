"""Lesson 13.1.6: CIPT Lite as a service, called end to end with no network.

S3 is moto's in-memory fake, reached with moto's fake credentials; the job log is a SQLite file in
a temporary folder; the API is called through FastAPI's TestClient. The program stores GridCap
medium's snapshot, solves it as a job, and asks for its NPV-risk frontier. GridCap is fictional.
"""

from __future__ import annotations

import os
import tempfile
import time
import warnings
from pathlib import Path

# Starlette 1.10 warns that its TestClient will move from httpx to httpx2; it works the same (F61).
warnings.filterwarnings("ignore", message="Using `httpx`")

for name, value in {"AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing",
                    "AWS_SECURITY_TOKEN": "testing", "AWS_SESSION_TOKEN": "testing",
                    "AWS_DEFAULT_REGION": "us-east-1"}.items():
    os.environ[name] = value                       # moto's fake credentials: never a real account

import boto3                                        # noqa: E402
from fastapi.testclient import TestClient           # noqa: E402
from moto import mock_aws                           # noqa: E402

from cipt_service import JobTable, S3Store, create_app   # noqa: E402
from gridcap import generate                        # noqa: E402

BUCKET = "cipt-lite-example"


def wait(client: TestClient, job_id: str) -> tuple[int, str]:
    """Poll until the job finishes; return how many polls answered 'not finished', and the state."""
    polls = 0
    while not (body := client.get(f"/jobs/{job_id}").json())["finished"]:
        polls += 1
        time.sleep(0.05)
    return polls, body["state"]


if __name__ == "__main__":
    with mock_aws(), tempfile.TemporaryDirectory() as tmp:
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET)
        store = S3Store(s3, BUCKET)
        client = TestClient(create_app(store, JobTable(Path(tmp) / "jobs.sqlite")))

        medium = generate("medium")
        r = client.post("/snapshots", json=medium.to_dict())
        snapshot = r.json()["snapshot"]
        print(f"POST /snapshots  -> {r.status_code}, snapshot {snapshot[:12]}")
        again = client.post("/snapshots", json=medium.to_dict()).json()["snapshot"]
        keys = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]]
        print(f"posted again     -> same snapshot {again == snapshot}; objects in S3: {len(keys)}")
        broken = medium.to_dict()
        broken["projects"][49]["parent"], broken["projects"][50]["parent"] = "P051", "P050"
        r = client.post("/snapshots", json=broken)
        print(f"a parent cycle   -> {r.status_code}, {r.json()['detail']}")

        r = client.post("/jobs", json={"snapshot": snapshot})
        job = r.json()["job_id"]
        early = client.get(f"/jobs/{job}/result").status_code
        print(f"POST /jobs       -> {r.status_code}, Location {r.headers['location'].replace(job, '<id>')}; "
              f"fetch at once -> {early}")
        _, state = wait(client, job)
        print(f"GET /jobs/<id>   -> polled until finished: {state}")
        result = client.get(f"/jobs/{job}/result").json()
        print(f"GET result       -> {result['status']}, NPV {result['npv']:,.0f}, bound {result['bound']:,.0f}, "
              f"{len(result['starts'])} projects")
        r = client.post("/jobs", json={"snapshot": snapshot, "budget": {"2040": 5}})
        print(f"a year outside   -> {r.status_code}, {r.json()['detail']}")
        r = client.post("/jobs", json={"snapshot": snapshot, "budget": {"2027": 2_000}})
        wait(client, r.json()["job_id"])
        print(f"2027 cut to $2,000k -> {client.get(r.json()['result']).json()['status']}")

        r = client.post("/frontier", json={"snapshot": snapshot, "points": 5})
        print(f"POST /frontier   -> {r.status_code}, {len(r.json()['points'])} non-dominated points")
        print(f"   {'NPV ($k)':>10} {'risk removed ($k)':>18} {'projects':>9}")
        for p in r.json()["points"]:
            print(f"   {p['npv']:>10,} {p['risk']:>18,.1f} {p['projects']:>9}")
        print("S3 keys:", sorted(k.split("/")[0] + "/..." for k in
                                 {o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]}))
