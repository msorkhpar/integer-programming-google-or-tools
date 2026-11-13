"""The module 46 examples: the snapshot schema, the quality gate, and canonical digests."""

import copy
import json

import pytest
from pydantic import ValidationError

from canonical import canonical, digest, fixed
from gridcap import generate
from plan_model import outcome
from quality import blocked, gate, required
from snapshot import Snapshot, export, load, project
from store import Corrupted, SnapshotStore


@pytest.fixture(scope="module")
def doc():
    return export(generate("small"))


def planted(doc, edit):
    d = copy.deepcopy(doc)
    edit(d)
    return load(json.dumps(d))


def test_the_export_validates_and_solves_to_the_base_plan(doc):
    snap = load(json.dumps(doc))
    assert len(snap.projects) == 40
    assert outcome(snap) == "OPTIMAL, NPV $22,741k"
    assert gate(snap) == []


def test_unknown_keys_and_guessed_types_are_refused_but_allowed_on_request(doc):
    d = copy.deepcopy(doc)
    project(d, "P023")["lag"] = project(d, "P023").pop("parent_lag")
    with pytest.raises(ValidationError):
        load(json.dumps(d))
    assert Snapshot.model_validate_json(json.dumps(d), extra="ignore").projects[22].parent_lag == 0
    text = json.dumps(doc).replace('"amount": 8890', '"amount": "8890"', 1)
    with pytest.raises(ValidationError):
        load(text)
    assert Snapshot.model_validate_json(text, strict=False).budget[0].amount == 8890


def test_reference_problems_are_all_reported_together(doc):
    d = copy.deepcopy(doc)
    project(d, "P016")["parent"] = "P099"
    d["budget"].pop()
    with pytest.raises(ValidationError) as caught:
        load(json.dumps(d))
    assert "P099" in str(caught.value) and "year 2031" in str(caught.value)


def test_a_cycle_is_an_error_and_drops_both_projects_quietly(doc):
    snap = planted(doc, lambda d: project(d, "P015").update(parent="P016", parent_lag=1))
    assert outcome(snap) == "OPTIMAL, NPV $22,637k"
    assert blocked(gate(snap)) and gate(snap)[0].rule == "parent-cycle"


def test_a_must_do_child_whose_parent_is_too_early_blocks_an_infeasible_snapshot(doc):
    snap = planted(doc, lambda d: project(d, "P023").update(must_do=True, parent_lag=3))
    assert outcome(snap) == "INFEASIBLE"
    assert [f.rule for f in gate(snap) if f.severity == "error"] == ["parent-too-late"]
    assert required(snap) == {"P003", "P010", "P017", "P039", "P023", "P022"}


def test_every_error_rule_is_sound_on_the_planted_cases(doc):
    """Whenever an error fires on a case whose solve is OPTIMAL, it is a contract error (a cycle)."""
    edits = [lambda d: project(d, "P016").update(must_do=True),
             lambda d: project(d, "P016").update(parent_lag=2),
             lambda d: d["budget"][2].update(amount=7008)]
    for edit in edits:
        snap = planted(doc, edit)
        assert not blocked(gate(snap, load(json.dumps(doc))))
        assert outcome(snap).startswith("OPTIMAL")


def test_budgets_in_millions_are_blocked_and_explained_by_drift(doc):
    def in_m(d):
        d["budget"] = [{"year": b["year"], "amount": round(b["amount"] / 1000)} for b in d["budget"]]
    snap = planted(doc, in_m)
    findings = gate(snap, load(json.dumps(doc)))
    assert outcome(snap) == "INFEASIBLE"
    assert [f.rule for f in findings].count("budget-drift") == 5 and blocked(findings)


def test_the_canonical_digest_ignores_layout_and_order_but_not_content(doc):
    other = copy.deepcopy(doc)
    other["projects"].reverse()
    other["discount_rate"] = 0.7 / 10
    a, b = load(json.dumps(doc)), load(json.dumps(other, indent=2, sort_keys=True))
    assert digest(a) == digest(b)
    assert a.model_dump_json() != b.model_dump_json()
    swapped = copy.deepcopy(doc)
    swapped["projects"][38]["cost_profile"].reverse()
    assert digest(load(json.dumps(swapped))) != digest(a)


def test_the_digest_of_gridcap_small_is_pinned(doc):
    """The same bytes, and so the same digest, on every machine: a change here is deliberate."""
    assert digest(load(json.dumps(doc))) == "730c8b40b1ebdabec854a5b7157ef9dd9208c223e73c7f18020d15f5a00bf520"


def test_fixed_floats():
    assert fixed(0.1 + 0.2) == 0.3 and repr(fixed(-0.0)) == "0.0"
    with pytest.raises(ValueError):
        fixed(float("nan"))


def test_the_store_deduplicates_versions_and_refuses_an_edited_file(doc, tmp_path):
    store = SnapshotStore(tmp_path)
    snap = load(json.dumps(doc))
    key = store.put(snap, "first")
    assert store.put(load(json.dumps(doc, indent=1)), "again") == key
    assert len(store.versions(snap.name)) == 1
    assert digest(store.get(key)) == key          # same content; records come back in canonical order
    assert canonical(store.get(key)) == (tmp_path / f"{key}.json").read_bytes()
    path = tmp_path / f"{key}.json"
    path.write_bytes(path.read_bytes().replace(b'"amount":8890', b'"amount":8891'))
    with pytest.raises(Corrupted):
        store.get(key)
