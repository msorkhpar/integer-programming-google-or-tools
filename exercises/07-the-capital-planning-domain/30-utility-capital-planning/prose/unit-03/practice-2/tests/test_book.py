from book import checked, copy, create, edit, lock, optimized

# A water utility's scenarios. Not the lesson's.


def test_a_scenario_walks_the_four_stages():
    book = {}
    assert create(book, "base", {"budget": 900})
    assert book["base"]["stage"] == "Initial" and book["base"]["plan"] is None
    assert checked(book, "base") and book["base"]["stage"] == "Pre-Opt"
    assert optimized(book, "base", {"W1": 2027}) and book["base"]["stage"] == "Post-Opt"
    assert book["base"]["plan"] == {"W1": 2027}
    assert lock(book, "base") and book["base"]["stage"] == "Budget Lock"


def test_steps_out_of_order_are_refused():
    book = {}
    assert create(book, "base", {"budget": 900})
    assert not create(book, "base", {"budget": 1})
    assert not optimized(book, "base", {"W1": 2027})
    assert not lock(book, "base")
    assert checked(book, "base") and not checked(book, "base")
    assert not lock(book, "base")
    assert book["base"]["stage"] == "Pre-Opt" and book["base"]["inputs"] == {"budget": 900}


def test_a_locked_scenario_refuses_edits_and_a_copy_does_not():
    book = {}
    assert create(book, "base", {"budget": 900}) and checked(book, "base")
    assert optimized(book, "base", {"W1": 2027}) and lock(book, "base")
    assert not edit(book, "base", {"budget": 800})
    assert book["base"]["inputs"] == {"budget": 900}
    assert copy(book, "base", "cut") and book["cut"]["parent"] == "base" and book["cut"]["stage"] == "Initial"
    assert edit(book, "cut", {"budget": 800}) and book["cut"]["inputs"] == {"budget": 800}


def test_editing_after_a_run_sends_it_back_and_drops_the_plan():
    book = {}
    assert create(book, "base", {"budget": 900}) and checked(book, "base")
    assert optimized(book, "base", {"W1": 2027})
    assert edit(book, "base", {"force_in": ["W4"]})
    assert book["base"]["stage"] == "Pre-Opt" and book["base"]["plan"] is None
    assert not lock(book, "base")


def test_a_copy_has_its_own_inputs():
    book = {}
    assert create(book, "base", {"budget": 900})
    assert copy(book, "base", "high")
    assert edit(book, "high", {"budget": 1_200})
    assert book["base"]["inputs"] == {"budget": 900} and book["high"]["inputs"] == {"budget": 1_200}


def test_only_one_plan_of_record():
    book = {}
    for name in ("a", "b"):
        assert create(book, name, {"budget": 900}) and checked(book, name)
        assert optimized(book, name, {"W1": 2027})
    assert lock(book, "a")
    assert not lock(book, "b") and book["b"]["stage"] == "Post-Opt"
