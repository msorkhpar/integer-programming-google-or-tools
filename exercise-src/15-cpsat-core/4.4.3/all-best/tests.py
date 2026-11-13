import itertools

from ortools.sat.python import cp_model

from best_plans import all_best

# A conference programme committee's talks (not the lesson's portfolio): score, minutes, track.
TALKS = {"T1": (5, 30, "data"), "T2": (3, 20, "data"), "T3": (4, 30, "web"), "T4": (2, 10, "web"),
         "T5": (4, 20, "ops"), "T6": (1, 10, "ops"), "T7": (3, 20, "ops")}


def programme(minutes: int, tracks_once: bool = True, with_spare: bool = False):
    """The talks that fit the session; at most one talk per track when tracks_once."""
    model = cp_model.CpModel()
    x = {t: model.new_bool_var(t) for t in TALKS}
    used = sum(m * x[t] for t, (_, m, _) in TALKS.items())
    model.add(used <= minutes)
    if tracks_once:
        for track in {k for _, _, k in TALKS.values()}:
            model.add_at_most_one(x[t] for t, (_, _, k) in TALKS.items() if k == track)
    if with_spare:
        spare = model.new_int_var(0, minutes, "spare")      # minutes left over, a variable outside the plan
        model.add(spare <= minutes - used)
    return model, x, sum(s * x[t] for t, (s, _, _) in TALKS.items())


def brute(minutes: int, tracks_once: bool = True):
    names = list(TALKS)
    plans = []
    for r in range(len(names) + 1):
        for plan in itertools.combinations(names, r):
            if sum(TALKS[t][1] for t in plan) > minutes:
                continue
            tracks = [TALKS[t][2] for t in plan]
            if tracks_once and len(tracks) != len(set(tracks)):
                continue
            plans.append(plan)
    best = max(sum(TALKS[t][0] for t in plan) for plan in plans)
    return best, sorted(tuple(sorted(p)) for p in plans if sum(TALKS[t][0] for t in p) == best)


def test_a_single_best_plan():
    model, x, score = programme(60)
    best, plans = brute(60)
    assert len(plans) == 1
    assert all_best(model, x, score) == (best, plans)


def test_the_best_score_with_ties():
    model, x, score = programme(50, tracks_once=False)
    assert all_best(model, x, score)[0] == brute(50, tracks_once=False)[0]


def test_every_tied_plan_is_returned():
    model, x, score = programme(50, tracks_once=False)
    best, plans = brute(50, tracks_once=False)
    assert len(plans) > 1
    assert all_best(model, x, score) == (best, plans)


def test_a_variable_outside_the_plan_does_not_repeat_plans():
    model, x, score = programme(45, with_spare=True)      # the best plans leave minutes over
    assert all_best(model, x, score) == brute(45)
