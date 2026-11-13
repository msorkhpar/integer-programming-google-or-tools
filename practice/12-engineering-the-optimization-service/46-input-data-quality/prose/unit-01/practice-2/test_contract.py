import json

from contract import parse

# A transit agency's fleet export (money in $k), in the current version 3 and the older version 2.
V3 = {"schema_version": 3, "buses": [
    {"bus_id": "B101", "depot": "North", "cost": 450, "must_replace": True},
    {"bus_id": "B102", "depot": "Harbor", "cost": 480, "must_replace": False}]}
V2 = {"schema_version": 2, "buses": [
    {"bus_id": "B201", "garage": "North", "cost": 300},
    {"bus_id": "B202", "garage": "Harbor", "cost": 320}]}


def sent(doc: dict) -> str:
    return json.dumps(doc)


def test_a_current_document_is_accepted_and_an_unknown_key_refused():
    fleet = parse(sent(V3))
    assert fleet is not None and fleet.buses[0].cost == 450 and fleet.buses[0].must_replace is True
    renamed = {**V3, "buses": [{**V3["buses"][0], "price": 450}, V3["buses"][1]]}
    assert parse(sent(renamed)) is None


def test_a_number_sent_as_text_is_refused():
    assert parse(sent(V3)) is not None
    as_text = {**V3, "buses": [{**V3["buses"][0], "cost": "450"}, V3["buses"][1]]}
    assert parse(sent(as_text)) is None


def test_a_flag_sent_as_text_is_refused():
    assert parse(sent(V3)) is not None
    as_text = {**V3, "buses": [{**V3["buses"][0], "must_replace": "yes"}, V3["buses"][1]]}
    assert parse(sent(as_text)) is None


def test_a_version_2_document_is_upgraded():
    fleet = parse(sent(V2))
    assert fleet is not None
    assert [b.depot for b in fleet.buses] == ["North", "Harbor"]
    assert [b.must_replace for b in fleet.buses] == [False, False]
    assert fleet.schema_version == 3


def test_an_unknown_key_in_a_version_2_document_is_still_refused():
    assert parse(sent(V2)) is not None
    extra = {**V2, "buses": [{**V2["buses"][0], "colour": "red"}, V2["buses"][1]]}
    assert parse(sent(extra)) is None


def test_a_version_2_document_with_version_3_keys_is_refused():
    assert parse(sent(V2)) is not None
    flagged = {**V2, "buses": [{**V2["buses"][0], "must_replace": True}, V2["buses"][1]]}
    both = {**V2, "buses": [{**V2["buses"][0], "depot": "South"}, V2["buses"][1]]}
    assert parse(sent(flagged)) is None
    assert parse(sent(both)) is None


def test_a_version_1_document_is_refused():
    v1 = {**V3, "schema_version": 1}
    assert parse(sent(V3)) is not None
    assert parse(sent(v1)) is None
