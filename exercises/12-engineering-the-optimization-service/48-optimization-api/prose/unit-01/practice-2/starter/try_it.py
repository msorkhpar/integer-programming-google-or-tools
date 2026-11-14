"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from trim_select import app

client = TestClient(app)
for noisy in ("httpx", "asyncio"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
circuits = [
    {"circuit_id": "F-7", "cost": 250, "risk_reduction": 60.0},
    {"circuit_id": "F-8", "cost": 200, "risk_reduction": 55.0},
    {"circuit_id": "F-9", "cost": 150, "risk_reduction": 30.0},
]


def post(budget, must_trim=()):
    r = client.post("/selections", json={"budget": budget, "circuits": circuits, "must_trim": list(must_trim)})
    return r.status_code, r.json()


print("budget 400:", post(400))
print("budget 400, must trim F-9:", post(400, ["F-9"]))
print("budget 300, must trim F-7 and F-8:", post(300, ["F-7", "F-8"]))
print("budget 400, must trim F-1:", post(400, ["F-1"])[0])
