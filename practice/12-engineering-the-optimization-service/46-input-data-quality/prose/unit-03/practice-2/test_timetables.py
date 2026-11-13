import hashlib

from timetables import Store, canonical

# A bus operator's route timetables; departures are in time order, so their order matters.
WINTER = {"route": "12", "depot": "North", "departures": ["06:10", "06:40", "07:10"]}
CUT = {"route": "12", "depot": "North", "departures": ["06:10", "07:10"]}


def tamper(store: Store, key: str) -> None:
    store.files[key] = store.files[key].replace(b"06:10", b"06:15")


def test_a_timetable_is_stored_under_its_digest_and_read_back():
    store = Store()
    key = store.put(WINTER, "winter")
    assert key == hashlib.sha256(canonical(WINTER)).hexdigest()
    assert store.get(key) == WINTER
    assert store.versions("winter") == [{"scenario": "winter", "version": 1, "digest": key, "parent": None}]


def test_the_same_content_sent_twice_is_one_file_and_one_version():
    store = Store()
    first = store.put(WINTER, "winter")
    again = store.put(dict(reversed(list(WINTER.items()))), "winter")
    assert again == first and len(store.files) == 1 and len(store.versions("winter")) == 1


def test_going_back_to_earlier_content_is_a_new_version():
    store = Store()
    a, b = store.put(WINTER, "winter"), store.put(CUT, "winter")
    assert store.put(WINTER, "winter") == a
    assert [(e["version"], e["digest"], e["parent"]) for e in store.versions("winter")] == \
        [(1, a, None), (2, b, a), (3, a, b)]
    assert len(store.files) == 2


def test_an_edited_file_is_refused():
    store = Store()
    key = store.put(WINTER, "winter")
    assert store.get(key) == WINTER
    tamper(store, key)
    assert store.get(key) is None


def test_each_scenario_has_its_own_versions():
    store = Store()
    a, b = store.put(WINTER, "winter"), store.put(CUT, "cut")
    assert store.versions("cut") == [{"scenario": "cut", "version": 1, "digest": b, "parent": None}]
    assert store.versions("winter") == [{"scenario": "winter", "version": 1, "digest": a, "parent": None}]


def test_a_stored_file_is_never_rewritten():
    store = Store()
    key = store.put(WINTER, "winter")
    assert store.get(key) == WINTER
    tamper(store, key)
    store.put(WINTER, "winter")
    assert store.get(key) is None
