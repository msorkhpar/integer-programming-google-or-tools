from replay import in_force


def entry(seq, action, project="", kind="", year=None, by="engineer-a"):
    return {"seq": seq, "action": action, "project": project, "kind": kind, "year": year, "by": by, "why": "w"}


def test_set_entries_are_in_force():
    trail = [entry(1, "set", "M-12", "start_in", 2028), entry(2, "set", "M-40", "out")]
    assert in_force(trail) == {"M-12": ("start_in", 2028), "M-40": ("out", None)}


def test_a_later_set_on_the_same_project_replaces_the_earlier_one():
    trail = [entry(1, "set", "M-12", "start_in", 2028), entry(2, "set", "M-12", "start_in", 2030)]
    assert in_force(trail) == {"M-12": ("start_in", 2030)}


def test_entries_are_replayed_by_sequence_number_not_list_position():
    trail = [entry(5, "set", "M-12", "start_in", 2030), entry(2, "set", "M-12", "start_in", 2028),
             entry(3, "set", "M-07", "out")]
    assert in_force(trail) == {"M-12": ("start_in", 2030), "M-07": ("out", None)}


def test_revoked_and_refused_entries_leave_nothing_behind():
    trail = [entry(1, "set", "M-12", "start_in", 2028), entry(2, "revoke", "M-12", "start_in", 2028),
             entry(3, "refused", "M-33", "start_in", 2040), entry(4, "set", "M-07", "out")]
    assert in_force(trail) == {"M-07": ("out", None)}


def test_a_clear_entry_ends_everything_set_before_it():
    trail = [entry(1, "set", "M-12", "start_in", 2028), entry(2, "inherit", "M-40", "out"),
             entry(3, "clear", by="manager-a"), entry(4, "set", "M-07", "out")]
    assert in_force(trail) == {"M-07": ("out", None)}
