"""Run: plan the tiny season and print the vegetation manager's report, then the same season under a
planner's override it can keep and under two overrides that clash, then whether two runs of the
season give the same record, then the season planned through the service and read back from its store.

The season is GridCap tiny, six circuits of a fictional utility, drawn by vegcrew/generate.py from
seed 54. Nothing is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

import warnings

from vegcrew.__main__ import main
from vegcrew.data import Override, season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
from vegcrew.record import dumps, fingerprint, plan_record
from vegcrew.report import format_plan

SIZE, SEED = "tiny", 54


def show_overrides() -> None:
    """The plan with one override it keeps, then the rules named when two overrides clash."""
    season = season_from_dict(scenario(SIZE, SEED))
    kept = (Override("skip", "C03", reason="road closed"),)
    clash = (Override("pin", "C01", crew="K1", start=12, reason="crew is nearby"),
             Override("pin", "C05", crew="K1", start=13, reason="landowner asked"))
    for title, overrides in (("skip C03:", kept), ("pin C01 and C05 a week apart on K1:", clash)):
        print()
        print(title)
        print(format_plan(season, make_plan(season, overrides)))


def show_record() -> None:
    """The season's input fingerprint, and whether two runs give records equal byte for byte."""
    raw = scenario(SIZE, SEED)
    season = season_from_dict(raw)
    runs = [dumps(plan_record(raw, make_plan(season))) for _ in range(2)]
    print()
    print(f"input sha256 {fingerprint(raw)[:12]}, records of two runs identical: {'yes' if runs[0] == runs[1] else 'no'}")


def show_service() -> None:
    """POST the season to the service, in-process, and GET its plan back by number."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")            # Starlette's deprecation notice about httpx
        from fastapi.testclient import TestClient
    from vegcrew.api import create_app

    api = TestClient(create_app(":memory:"))
    reply = api.post("/plans", json={"season": scenario(SIZE, SEED)})
    body = reply.json()
    print()
    print(f"POST /plans -> {reply.status_code}, id {body['id']}, {body['record']['status']}, "
          f"risk carried ${body['record']['risk_carried']:,}k")
    again = api.get(f"/plans/{body['id']}")
    print(f"GET /plans/{body['id']} -> {again.status_code}, same body: {again.json() == body}")
    print(f"GET /plans/7 -> {api.get('/plans/7').status_code}")


if __name__ == "__main__":
    main([SIZE, "--seed", str(SEED)])
    show_overrides()
    show_record()
    show_service()
