"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from trim_api import app

client = TestClient(app)
for noisy in ("httpx", "asyncio"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def post(budget, circuits):
    r = client.post("/trims", json={"budget": budget, "circuits": circuits})
    return r.status_code, r.json() if r.status_code == 200 else ""


line = {"circuit_id": "F-41", "miles": 6.5, "cost": 210}
print("budget 500, one circuit:", post(500, [line]))
print("budget 0, two circuits:", post(0, [line, {**line, "circuit_id": "F-42"}]))
print("budget -10:", post(-10, [line]))
print("miles 0:", post(500, [{**line, "miles": 0}]))
print("F-41 twice:", post(500, [line, line]))
print("no circuits:", post(500, []))
