"""A planner tool's side of the API: its own small model of the result, and the table it draws.

GridCap is fictional. The tool declares only the fields it reads. Pydantic ignores fields a model
does not declare (its default), so the service may add fields without breaking the tool.
"""

import json
import warnings
from collections import Counter

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi.testclient import TestClient  # noqa: E402
from pydantic import BaseModel, ValidationError  # noqa: E402

from job_api import create_app  # noqa: E402
from jobs import JobStore  # noqa: E402


class Row(BaseModel):
    project_id: str
    start_year: int
    program: str
    capex: int


class Year(BaseModel):
    year: int
    spend: int
    budget: int
    headroom: int


class PlannerView(BaseModel):          # the tool's model: no bound, no snapshot, no region
    status: str
    message: str
    npv: float | None
    gap: float | None
    plan: list[Row]
    spend_by_year: list[Year]


store = JobStore()
client = TestClient(create_app(store))
job_id = client.post("/jobs", json={"portfolio": "small", "budget": {"2029": 7000}}).json()["job_id"]
store.outcome(store.get(job_id))
body = client.get(f"/jobs/{job_id}/result").text

view = PlannerView.model_validate_json(body)
print(f"[{view.status}] {view.message}")
print(f"{'year':<6}{'spend':>8}{'budget':>8}{'headroom':>10}")
for y in view.spend_by_year:
    print(f"{y.year:<6}{y.spend:>8,}{y.budget:>8,}{y.headroom:>10,}")
for program, count in sorted(Counter(r.program for r in view.plan).items()):
    capex = sum(r.capex for r in view.plan if r.program == program)
    print(f"{program:<13} {count:>2} projects  ${capex:,}k")

renamed = json.loads(body)
renamed["npv_k"] = renamed.pop("npv")         # the service renames a field the tool reads
try:
    PlannerView.model_validate(renamed)
except ValidationError as error:
    print("after renaming npv:", error.errors()[0]["loc"], error.errors()[0]["msg"])
added = {**json.loads(body), "region_spend": {"Valley": 1}}    # the service adds a field
print("after adding a field:", PlannerView.model_validate(added).status)
