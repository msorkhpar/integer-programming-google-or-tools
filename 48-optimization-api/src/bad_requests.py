"""What lesson 12.4.1's API answers to requests it cannot accept: 422 for bad input, 404 for an unknown name."""

import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi.testclient import TestClient  # noqa: E402

from plan_api import app  # noqa: E402

client = TestClient(app)

bad = {
    "negative budget": {"portfolio": "tiny", "budget": {"2028": -100}},
    "zero time limit": {"portfolio": "tiny", "time_limit_s": 0},
    "unknown portfolio": {"portfolio": "huge"},
    "misspelled field": {"portfolio": "tiny", "budgets": {"2028": 900}},
    "year as text": {"portfolio": "tiny", "budget": {"next year": 900}},
}
for label, body in bad.items():
    r = client.post("/plans", json=body)
    error = r.json()["detail"][0]
    print(f"{label:<18} -> {r.status_code}  at {error['loc']}: {error['msg']}")

r = client.post("/plans", json={"portfolio": "tiny", "budget": {"2035": 900}})
print(f"{'year outside plan':<18} -> {r.status_code}  {r.json()['detail']}")
r = client.get("/portfolios/huge")
print(f"{'GET unknown name':<18} -> {r.status_code}  {r.json()['detail']}")
