import itertools

from ortools.math_opt.python import mathopt

from programme import Talk, build

# A training week's talks (not GridCap): one shared lab of 10 hours, each speaker gives one talk.
TALKS = [Talk("A", "kim", 6, 5), Talk("B", "lee", 6, 4), Talk("C", "mo", 6, 4),
         Talk("D", "ola", 2, 3), Talk("E", "nia", 3, 2)]


def accepted_ok(talks, lab, chosen) -> bool:
    model, x = build(talks, lab)
    for name, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if name in chosen else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def truly_ok(talks, lab, chosen) -> bool:
    picked = [t for t in talks if t.name in chosen]
    return (len({t.speaker for t in picked}) == len(picked)
            and all(a.lab_hours + b.lab_hours <= lab for a, b in itertools.combinations(picked, 2)))


def same_plans(talks, lab) -> bool:
    names = [t.name for t in talks]
    return all(accepted_ok(talks, lab, set(c)) == truly_ok(talks, lab, set(c))
               for r in range(len(names) + 1) for c in itertools.combinations(names, r))


def lp_bound(talks, lab) -> float:
    model, _ = build(talks, lab, integer=False)
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_every_programme_the_rules_allow_is_allowed_and_no_other():
    # A, B and C each need 6 of the 10 lab hours, so any two of them overrun.
    assert same_plans(TALKS, 10)


def test_one_speaker_two_talks_clash_even_with_lab_room():
    talks = [Talk("A", "kim", 1, 5), Talk("B", "kim", 1, 4), Talk("C", "lee", 1, 1)]
    assert accepted_ok(talks, 10, {"A", "C"}) is True
    assert accepted_ok(talks, 10, {"A", "B"}) is False


def test_two_talks_that_exactly_fill_the_lab_may_both_run():
    talks = [Talk("A", "kim", 5, 5), Talk("B", "lee", 5, 4), Talk("C", "mo", 6, 1)]
    assert accepted_ok(talks, 10, {"A", "B"}) is True
    assert accepted_ok(talks, 10, {"A", "C"}) is False


def test_talks_that_clash_two_by_two_share_one_row():
    # A, B and C clash two by two. With one row for the three, the LP's best is the plan A, D, E
    # worth 10; with a row per pair it could take A, B and C at 0.5 each, for 11.5.
    assert lp_bound(TALKS, 10) <= 10 + 1e-6
    # A and D share a speaker, A and B overrun the lab, B and D too: one row for all three.
    talks = [Talk("A", "kim", 6, 5), Talk("B", "lee", 6, 5), Talk("D", "kim", 5, 5), Talk("E", "nia", 1, 1)]
    assert same_plans(talks, 10)
    assert lp_bound(talks, 10) <= 5 + 1 + 1e-6
