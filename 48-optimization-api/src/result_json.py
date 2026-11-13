"""What a planner tool receives from GET /jobs/{id}/result, for a proven plan and for no plan.

GridCap is fictional. The small portfolio's must-do P017 costs $5,310k in 2030 or 2031, so budgets
of $5,000k in both years leave no plan.
"""

import json
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi.testclient import TestClient  # noqa: E402

from job_api import create_app  # noqa: E402
from jobs import JobStore  # noqa: E402

store = JobStore()
client = TestClient(create_app(store))


def finished_result(body: dict) -> dict:
    job_id = client.post("/jobs", json=body).json()["job_id"]
    store.outcome(store.get(job_id))            # wait for the job
    return client.get(f"/jobs/{job_id}/result").json()


proven = finished_result({"portfolio": "small"})
shown = {**proven, "plan": proven["plan"][:2] + [f"... {len(proven['plan']) - 2} more"]}
print(json.dumps(shown, indent=1))

none = finished_result({"portfolio": "small", "budget": {"2030": 5000, "2031": 5000}})
print(json.dumps(none, indent=1))
