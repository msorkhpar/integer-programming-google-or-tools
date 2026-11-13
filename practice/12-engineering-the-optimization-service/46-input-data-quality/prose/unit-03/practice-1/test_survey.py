import copy
import json

from survey import digest

# A pipe-inspection survey: segments with wall-thickness readings (mm) taken in order along the pipe.
SURVEY = {
    "version": 1,
    "survey": "Riverside",
    "rate": 0.05,
    "tags": ["cast-iron", "priority"],
    "segments": [
        {"id": "S2", "material": "Gußeisen", "length_m": 120.5, "readings": [2.1, 2.05, 1.9]},
        {"id": "S1", "material": "ductile", "length_m": 80.0, "readings": [3.0, 2.95]},
    ],
}


def changed(edit) -> dict:
    doc = copy.deepcopy(SURVEY)
    edit(doc)
    return doc


def refused(doc: dict) -> bool:
    try:
        digest(doc)
    except ValueError:
        return True
    return False


def test_key_order_and_layout_do_not_matter_but_a_reading_does():
    relaid = json.loads(json.dumps(SURVEY, indent=4, sort_keys=True))
    reordered = dict(reversed(list(relaid.items())))
    assert digest(reordered) == digest(SURVEY)
    assert digest(changed(lambda d: d["segments"][0]["readings"].__setitem__(1, 2.06))) != digest(SURVEY)


def test_segments_in_another_order_are_the_same_survey():
    assert digest(changed(lambda d: d["segments"].reverse())) == digest(SURVEY)


def test_tags_in_another_order_are_the_same_survey():
    assert digest(changed(lambda d: d["tags"].reverse())) == digest(SURVEY)


def test_readings_keep_their_order():
    assert digest(changed(lambda d: d["segments"].reverse())) == digest(SURVEY)
    assert digest(changed(lambda d: d["segments"][0]["readings"].reverse())) != digest(SURVEY)


def test_floats_equal_to_three_decimals_are_the_same():
    assert digest(changed(lambda d: d.update(rate=0.1 + 0.2))) == digest(changed(lambda d: d.update(rate=0.3)))


def test_minus_zero_is_zero():
    assert digest(changed(lambda d: d.update(rate=-0.0))) == digest(changed(lambda d: d.update(rate=0.0)))


def test_nan_is_refused():
    assert not refused(SURVEY)
    assert refused(changed(lambda d: d.update(rate=float("nan"))))


def test_the_digest_is_the_documented_one():
    assert digest(SURVEY) == "ae0963e1f1c60d571a638c3ed681a4bcbda8e1bfa638392c6df95851a18aa015"
