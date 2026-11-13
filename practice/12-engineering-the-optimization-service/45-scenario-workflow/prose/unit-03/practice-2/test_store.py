from store import Store


def fresh() -> Store:
    s = Store()
    s.create("D-1", {"roofs": 400, "boilers": 250})
    return s


def test_a_save_from_the_current_version_is_stored():
    s = fresh()
    plan, v = s.read("D-1")
    plan["roofs"] = 350
    assert s.save("D-1", v, plan) == 2
    assert s.read("D-1") == ({"roofs": 350, "boilers": 250}, 2)


def test_a_save_from_an_old_version_is_refused_and_changes_nothing():
    s = fresh()
    a, va = s.read("D-1")
    b, vb = s.read("D-1")
    a["roofs"] = 350
    b["boilers"] = 300
    assert s.save("D-1", va, a) == 2
    assert s.save("D-1", vb, b) is None
    assert s.read("D-1") == ({"roofs": 350, "boilers": 250}, 2)


def test_editing_what_read_returned_changes_nothing_stored():
    s = fresh()
    plan, v = s.read("D-1")
    plan["roofs"] = 0
    assert s.read("D-1") == ({"roofs": 400, "boilers": 250}, 1)
    assert s.save("D-1", v, plan) == 2


def test_editing_a_plan_after_saving_it_changes_nothing_stored():
    s = fresh()
    plan, v = s.read("D-1")
    plan["roofs"] = 350
    s.save("D-1", v, plan)
    plan["roofs"] = 1
    assert s.read("D-1") == ({"roofs": 350, "boilers": 250}, 2)
