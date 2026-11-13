import copy
import json

from pydantic import ValidationError

from fleet import FleetSnapshot

# A city transit agency's bus-replacement snapshot (money in $k). Not the lesson's portfolio.
CLEAN = {
    "schema_version": 3,
    "horizon": [2027, 2028, 2029],
    "depots": ["North", "Harbor"],
    "budgets": [{"year": 2027, "amount": 900}, {"year": 2028, "amount": 600}, {"year": 2029, "amount": 1200}],
    "buses": [
        {"bus_id": "B101", "depot": "North", "cost": 450, "earliest": 2027, "latest": 2028},
        {"bus_id": "B102", "depot": "Harbor", "cost": 480, "earliest": 2028, "latest": 2029},
        {"bus_id": "B103", "depot": "Harbor", "cost": 510, "earliest": 2027, "latest": 2029},
    ],
}


def verdict(doc: dict) -> str | None:
    """None if the snapshot is accepted, else the messages of the validation error."""
    try:
        FleetSnapshot.model_validate_json(json.dumps(doc))
    except ValidationError as error:
        return "; ".join(e["msg"] for e in error.errors())
    return None


def changed(edit) -> dict:
    doc = copy.deepcopy(CLEAN)
    edit(doc)
    return doc


def test_a_clean_snapshot_is_accepted_and_a_duplicate_bus_refused():
    assert verdict(CLEAN) is None
    error = verdict(changed(lambda d: d["buses"].append(dict(d["buses"][0]))))
    assert error is not None and "B101" in error


def test_a_bus_at_an_unlisted_depot_is_refused_by_name():
    error = verdict(changed(lambda d: d["buses"][2].update(depot="Airport")))
    assert error is not None and "B103" in error


def test_a_horizon_year_without_a_budget_is_refused():
    error = verdict(changed(lambda d: d["budgets"].pop(1)))
    assert error is not None and "2028" in error


def test_a_year_with_two_budget_rows_is_refused():
    error = verdict(changed(lambda d: d["budgets"].append({"year": 2029, "amount": 300})))
    assert error is not None and "2029" in error


def test_every_problem_is_reported_in_one_error():
    def two(d):
        d["buses"][1]["depot"] = "Airport"
        d["budgets"].pop(0)
    error = verdict(changed(two))
    assert error is not None and "B102" in error and "2027" in error


def test_a_reversed_window_is_refused_and_a_one_year_window_accepted():
    assert verdict(changed(lambda d: d["buses"][0].update(earliest=2028, latest=2028))) is None
    assert verdict(changed(lambda d: d["buses"][0].update(earliest=2029, latest=2028))) is not None


def test_a_zero_budget_is_accepted_and_a_negative_one_refused():
    assert verdict(changed(lambda d: d["budgets"][1].update(amount=0))) is None
    assert verdict(changed(lambda d: d["budgets"][1].update(amount=-50))) is not None


def test_a_bus_that_costs_nothing_is_refused():
    assert verdict(changed(lambda d: d["buses"][0].update(cost=1))) is None
    assert verdict(changed(lambda d: d["buses"][0].update(cost=0))) is not None
