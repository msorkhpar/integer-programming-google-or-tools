"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")
from fastapi.testclient import TestClient  # noqa: E402

from frontier_endpoint import best, create_app, frontier  # noqa: E402


def job(cost, npv, risk):
    return {"cost": cost, "earliest": 2031, "latest": 2031, "must": False, "parent": None, "lag": 0,
            "group": None, "npv": {2031: npv}, "risk": {2031: risk}}


snapshot = {"years": [2031], "budget": {2031: 200}, "projects": {
    "S1": job([100], 70, 5), "S2": job([100], 50, 25), "S3": job([100], 20, 45), "S4": job([100], 10, 50)}}

print("most NPV, then risk:", best(snapshot, "npv", "risk", {}))
print("most risk, then NPV:", best(snapshot, "risk", "npv", {}))
for point in frontier(snapshot, 4):
    print("frontier point, 4 floors:", point)
with TestClient(create_app()) as client:
    reply = client.post("/frontier", json={"snapshot": snapshot, "points": 3})
    print("POST /frontier points=3:", reply.status_code, [(p["npv"], p["risk"]) for p in reply.json().get("points", [])])
    print("POST /frontier points=20:", client.post("/frontier", json={"snapshot": snapshot, "points": 20}).status_code)
