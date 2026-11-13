import hashlib

from snapshot import changed_fields, snapshot_id

# A water utility's scenario inputs. Not the lesson's scenarios.


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


BASE = {"budget": {"2027": 900, "2028": 950}, "force_in": ["W1", "W2"], "force_out": [],
        "settings": {"gap": 0, "solver": "HIGHS"}}
BASE_TEXT = ('{"budget":{"2027":900,"2028":950},"force_in":["W1","W2"],"force_out":[],'
             '"settings":{"gap":0,"solver":"HIGHS"}}')


def test_the_id_is_the_sha256_of_the_canonical_text():
    assert snapshot_id(BASE) == sha(BASE_TEXT)
    assert snapshot_id({**BASE, "budget": {"2027": 900, "2028": 951}}) != sha(BASE_TEXT)


def test_changed_fields_names_what_differs():
    assert changed_fields(BASE, dict(BASE)) == []
    other = {**BASE, "budget": {"2027": 900, "2028": 800}, "settings": {"gap": 0.01, "solver": "HIGHS"}}
    assert changed_fields(BASE, other) == ["budget", "settings"]


def test_key_order_does_not_change_the_id():
    shuffled = {"settings": {"solver": "HIGHS", "gap": 0}, "force_out": [], "force_in": ["W1", "W2"],
                "budget": {"2028": 950, "2027": 900}}
    assert snapshot_id(shuffled) == sha(BASE_TEXT)


def test_override_order_does_not_change_the_id():
    assert snapshot_id({**BASE, "force_in": ["W2", "W1"]}) == sha(BASE_TEXT)
    assert changed_fields(BASE, {**BASE, "force_in": ["W2", "W1"], "force_out": ["W9"]}) == ["force_out"]


def test_a_field_only_one_side_has_is_a_change():
    assert changed_fields(BASE, {**BASE, "floor": {"North": 100}}) == ["floor"]


def test_text_outside_ascii_is_escaped():
    assert snapshot_id({"region": "C\u00f4te"}) == sha('{"region":"C\\u00f4te"}')
