"""The OpenAPI description FastAPI writes for lesson 12.4.1's API, read without starting a server."""

import json

from plan_api import PlanRequest, app

spec = app.openapi()
print("OpenAPI", spec["openapi"], "-", spec["info"]["title"], spec["info"]["version"])
for path, operations in spec["paths"].items():
    for method, op in operations.items():
        print(f"  {method.upper():<5} {path:<20} responses {sorted(op['responses'])}")

print("PlanRequest as JSON Schema:")
print(json.dumps(PlanRequest.model_json_schema(), indent=1))
