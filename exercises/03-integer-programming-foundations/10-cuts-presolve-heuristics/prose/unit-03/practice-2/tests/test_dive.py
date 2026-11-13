from dive import dive


def scripted(answers):
    """An LP that knows the answers to the calls a correct dive makes, and refuses any other call."""
    def lp(fixed):
        key = tuple(sorted(fixed.items()))
        assert key in answers, f"the dive asked for an LP with fixings {dict(key)}, which a correct dive never asks"
        return answers[key]
    return lp


def test_the_least_fractional_variable_is_rounded_up():
    lp = scripted({(): {"a": 1, "b": 0.9, "c": 0.4},
                   (("b", 1),): {"a": 1, "b": 1, "c": 0}})
    assert dive(lp) == ({"a": 1, "b": 1, "c": 0}, [("b", 1)])


def test_the_least_fractional_variable_is_rounded_down():
    lp = scripted({(): {"p": 0.1, "q": 0.6, "r": 0},
                   (("p", 0),): {"p": 0, "q": 1, "r": 1}})
    assert dive(lp) == ({"p": 0, "q": 1, "r": 1}, [("p", 0)])


def test_an_infeasible_fixing_is_tried_the_other_way():
    lp = scripted({(): {"a": 1, "b": 0.8},
                   (("b", 1),): None,
                   (("b", 0),): {"a": 1, "b": 0}})
    assert dive(lp) == ({"a": 1, "b": 0}, [("b", 0)])


def test_earlier_fixings_stay_in_every_later_lp():
    lp = scripted({(): {"a": 0.9, "b": 0.4},
                   (("a", 1),): {"a": 1, "b": 0.45},
                   (("a", 1), ("b", 0)): {"a": 1, "b": 0}})
    assert dive(lp) == ({"a": 1, "b": 0}, [("a", 1), ("b", 0)])


def test_a_dead_end_returns_only_the_fixings_kept():
    lp = scripted({(): {"a": 0.9, "b": 0.4},
                   (("a", 1),): {"a": 1, "b": 0.3},
                   (("a", 1), ("b", 0)): None,
                   (("a", 1), ("b", 1)): None})
    assert dive(lp) == (None, [("a", 1)])
