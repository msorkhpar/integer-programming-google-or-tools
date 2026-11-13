"""Call lesson 12.4.1's planning API through FastAPI's TestClient: no server, no port, no network."""

import json
import warnings

# Starlette 1.10 warns that its TestClient will move from httpx to httpx2; the client works the same.
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi.testclient import TestClient  # noqa: E402

from plan_api import app  # noqa: E402

client = TestClient(app)

r = client.get("/health")
print("GET /health ->", r.status_code, r.json())
r = client.get("/portfolios/tiny")
print("GET /portfolios/tiny ->", r.status_code, r.json())

r = client.post("/plans", json={"portfolio": "tiny"})
print("POST /plans tiny ->", r.status_code)
print(json.dumps(r.json(), indent=1))

r = client.post("/plans", json={"portfolio": "tiny", "budget": {"2028": 1000}})
print("POST /plans tiny, 2028 budget 1000 ->", r.status_code, r.json())
