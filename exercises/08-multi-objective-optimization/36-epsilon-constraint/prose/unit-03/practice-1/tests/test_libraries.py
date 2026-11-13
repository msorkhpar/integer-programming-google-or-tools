import itertools

from libraries import Upgrade, frontier

BRANCHES = [
    Upgrade("Eastside", 12, 20, 40),
    Upgrade("Harbor", 20, 5, 35),
    Upgrade("Old Town", 6, 30, 30),
    Upgrade("Mill Road", 9, 12, 20),
    Upgrade("Westgate", 15, 8, 25),
    Upgrade("Pine Hill", 4, 18, 15),
]


def scores(upgrades, budget):
    out = set()
    for k in range(len(upgrades) + 1):
        for pick in itertools.combinations(upgrades, k):
            if sum(u.cost for u in pick) <= budget:
                out.add((sum(u.hours for u in pick), sum(u.seats for u in pick)))
    return out


def dominates(p, q):
    return p[0] >= q[0] and p[1] >= q[1] and p != q


def by_hand(upgrades, budget):
    every = scores(upgrades, budget)
    return {q for q in every if not any(dominates(p, q) for p in every)}


def test_the_frontier_is_every_nondominated_score():
    assert set(frontier(BRANCHES, 90)) == by_hand(BRANCHES, 90)


def test_no_returned_point_dominates_another():
    tied = [Upgrade("North", 10, 0, 30), Upgrade("South", 10, 6, 30), Upgrade("Kiosk", 0, 4, 10),
            Upgrade("Annex", 3, 9, 25)]
    got = frontier(tied, 40)
    assert not [(p, q) for p in got for q in got if dominates(p, q)]
    assert set(got) == by_hand(tied, 40)


def test_a_choice_with_no_seats_can_be_on_the_frontier():
    late = [Upgrade("Night Desk", 30, 0, 50), Upgrade("Study Hall", 5, 25, 50)]
    assert (30, 0) in frontier(late, 50)


def test_each_score_is_listed_once():
    got = frontier(BRANCHES, 90)
    assert len(got) == len(set(got)) == len(by_hand(BRANCHES, 90))


def test_scores_come_sorted_by_hours():
    assert frontier(BRANCHES, 90) == sorted(by_hand(BRANCHES, 90))
