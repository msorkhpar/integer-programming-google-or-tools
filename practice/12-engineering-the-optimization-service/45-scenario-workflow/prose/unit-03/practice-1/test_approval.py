from approval import allowed, reachable, walk


def test_a_draft_is_edited_submitted_and_approved():
    assert walk("Draft", ["edit", "submit", "approve"]) == ("Approved", None)


def test_a_walk_stops_at_the_first_refused_action():
    assert walk("Draft", ["submit", "edit", "approve"]) == ("Submitted", "edit")


def test_the_actions_a_state_accepts():
    assert allowed("Submitted") == ["approve", "reject"]
    assert allowed("Archived") == []


def test_an_approved_program_can_never_return_to_draft():
    assert reachable("Approved") == ["Approved", "Archived"]


def test_a_draft_can_reach_every_state_through_several_steps():
    assert reachable("Draft") == ["Approved", "Archived", "Draft", "Submitted"]
