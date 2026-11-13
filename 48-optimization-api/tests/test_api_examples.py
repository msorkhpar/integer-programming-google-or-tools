"""The module 48 examples: the planning API, the job service, and the result schema."""

import threading

import pytest
from fastapi.testclient import TestClient
from ortools.math_opt.python import mathopt
from pydantic import ValidationError

from gridcap import generate
from job_api import create_app
from jobs import JobRequest, JobStore, Outcome, outcome_of, relative_gap, run_job
from plan_api import app as plan_app
from plan_model import build, spend_of
from schemas import PlanResult, to_result


def termination(reason, limit=None, primal=0.0, dual=0.0):
    return mathopt.SolveResult(termination=mathopt.Termination(
        reason=reason, limit=limit, objective_bounds=mathopt.ObjectiveBounds(primal, dual)))


# 12.4.1 -------------------------------------------------------------------------------------

def test_the_plan_endpoint_solves_tiny_within_its_budgets():
    body = TestClient(plan_app).post("/plans", json={"portfolio": "tiny"}).json()
    tiny = generate("tiny")
    assert body["status"] == "optimal" and body["npv"] == pytest.approx(2473)
    spend = spend_of(tiny, body["starts"])
    assert all(spend[y] <= tiny.budget[y] for y in tiny.years)


def test_an_infeasible_scenario_is_a_200_with_no_plan():
    r = TestClient(plan_app).post("/plans", json={"portfolio": "tiny", "budget": {"2028": 1000}})
    assert r.status_code == 200 and r.json()["status"] == "infeasible" and r.json()["starts"] == {}


@pytest.mark.parametrize("body", [{"portfolio": "tiny", "budget": {"2028": -1}}, {"portfolio": "tiny", "time_limit_s": 0},
                                  {"portfolio": "huge"}, {"portfolio": "tiny", "budgets": {}},
                                  {"portfolio": "tiny", "budget": {"2040": 5}}])
def test_bad_requests_are_422(body):
    assert TestClient(plan_app).post("/plans", json=body).status_code == 422


# 12.4.2 -------------------------------------------------------------------------------------

def test_terminations_map_to_their_own_statuses():
    R, L = mathopt.TerminationReason, mathopt.Limit
    assert outcome_of(termination(R.INFEASIBLE), {}, 5).status == "infeasible"
    assert outcome_of(termination(R.NO_SOLUTION_FOUND, L.TIME, dual=float("inf")), {}, 5).status == "time_limit"
    assert outcome_of(termination(R.NO_SOLUTION_FOUND, L.NODE), {}, 5).status == "failed"
    assert outcome_of(termination(R.OTHER_ERROR), {}, 5).status == "failed"


def test_the_worker_turns_a_solver_refusal_into_failed():
    assert run_job(JobRequest(portfolio="small")).status == "optimal"     # fixes HiGHS's thread count for the process
    out = run_job(JobRequest(portfolio="small", highs_threads=2))
    assert out.status == "failed" and "INTERNAL" in out.message and out.starts == {}


def test_the_worker_solves_small_and_reports_the_cut_as_infeasible():
    assert run_job(JobRequest(portfolio="small")).npv == pytest.approx(24260)
    assert run_job(JobRequest(portfolio="small", budget={2030: 5000, 2031: 5000})).status == "infeasible"


def test_relative_gap_is_zero_for_a_proven_plan_and_positive_otherwise():
    assert relative_gap(100.0, 100.0) == 0.0 and relative_gap(100.0, 110.0) == pytest.approx(0.1)


def test_submit_poll_fetch_with_a_held_worker():
    release = threading.Event()

    def held(request):
        release.wait(5)
        return Outcome("optimal", "done", {}, 0.0, 0.0, 0.0)

    store = JobStore(worker=held)
    client = TestClient(create_app(store))
    first = client.post("/jobs", json={"portfolio": "tiny"})
    second = client.post("/jobs", json={"portfolio": "tiny"})
    assert first.status_code == 202 and first.headers["location"] == "/jobs/job-1"
    assert second.json()["status"] == "queued"
    assert client.get("/jobs/job-2/result").status_code == 409
    assert client.get("/jobs/job-3").status_code == 404
    release.set()
    store.get("job-2").future.result()
    assert client.get("/jobs/job-2").json() == {"job_id": "job-2", "status": "optimal", "finished": True}


# 12.4.3 -------------------------------------------------------------------------------------

def test_a_result_reports_spend_within_budget_and_a_zero_gap():
    request = JobRequest(portfolio="small")
    result = to_result("job-1", request, run_job(request))
    assert result.gap == 0 and all(y.headroom >= 0 for y in result.spend_by_year)
    assert sum(r.npv for r in result.plan) == pytest.approx(result.npv)


def test_the_schema_refuses_an_infeasible_result_with_a_plan():
    with pytest.raises(ValidationError):
        PlanResult(job_id="j", snapshot="s", status="infeasible", message="m", npv=1.0, bound=1.0, gap=0.0,
                   plan=[], spend_by_year=[])


def test_equal_requests_have_equal_snapshots():
    a = to_result("a", JobRequest(portfolio="tiny", budget={2028: 3000}), Outcome("infeasible", "m"))
    b = to_result("b", JobRequest.model_validate_json('{"portfolio": "tiny", "budget": {"2028": 3000}}'),
                  Outcome("infeasible", "m"))
    assert a.snapshot == b.snapshot


def test_the_model_rows_carry_the_lesson_labels():
    pm = build(generate("tiny"), dict(generate("tiny").budget))
    names = {c.name for c in pm.model.linear_constraints()}
    assert {"budget_2027", "must_P002"} <= names
