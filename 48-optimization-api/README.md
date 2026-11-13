# 12.4. The Optimization API

Putting the planning model behind a REST API a planner tool can call: a FastAPI app with pydantic
requests, tested through `TestClient` with no server; long solves as jobs that are submitted,
polled and fetched, with a status for every way a solve can end and worker processes that survive a
solver crash; and a result schema with the plan, spend by year, NPV, gap, status and a message that
another team's code can rely on.

## Contents

1. [A REST API with FastAPI](README_12.4.1.md)
2. [Long solves: submit, poll, fetch](README_12.4.2.md)
3. [Result schemas planners can consume](README_12.4.3.md)
