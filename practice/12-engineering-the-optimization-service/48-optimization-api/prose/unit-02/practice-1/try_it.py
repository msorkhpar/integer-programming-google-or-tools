"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import time
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fastapi.testclient import TestClient

from crew_jobs import create_app

for noisy in ("httpx", "asyncio"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def solve(request):
    if request.weeks == 40:
        raise RuntimeError("holiday calendar for week 40 is missing")
    time.sleep(0.2)
    return {"status": "optimal", "crews_used": request.crews, "weeks": request.weeks}


client = TestClient(create_app(solve), raise_server_exceptions=False)
first = client.post("/jobs", json={"crews": 3, "weeks": 8}).json()
second = client.post("/jobs", json={"crews": 2, "weeks": 40}).json()
print("submit 3 crews, 8 weeks:", first.get("status"))
print("poll it right away:", client.get(f"/jobs/{first.get('job_id')}").json().get("status"))
print("fetch it right away:", client.get(f"/jobs/{first.get('job_id')}/result").status_code)
time.sleep(1.0)
print("fetch 3 crews, 8 weeks later:", client.get(f"/jobs/{first.get('job_id')}/result").json())
print("fetch 2 crews, 40 weeks later:", client.get(f"/jobs/{second.get('job_id')}/result").json())
print("poll job abc:", client.get("/jobs/abc").status_code)
