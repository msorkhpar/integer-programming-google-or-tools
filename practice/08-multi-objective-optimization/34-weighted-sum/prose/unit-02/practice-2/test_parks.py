from itertools import combinations

from parks import Project, unreachable


def scores(projects, budget):
    out = {}
    for size in range(len(projects) + 1):
        for chosen in combinations(projects, size):
            if sum(p.cost for p in chosen) <= budget:
                out[frozenset(p.name for p in chosen)] = (sum(p.shade for p in chosen),
                                                          sum(p.visits for p in chosen))
    return out


def assert_proved(projects, budget, answer):
    """`answer` is an unbeaten plan below the line between two other allowed plans."""
    assert answer is not None
    plan, a, b = (frozenset(x) for x in answer)
    allowed = scores(projects, budget)
    assert plan in allowed and a in allowed and b in allowed
    (nq, rq), (na, ra), (nb, rb) = allowed[plan], allowed[a], allowed[b]
    assert not any(n >= nq and r >= rq and (n, r) != (nq, rq) for n, r in allowed.values())
    assert na < nq < nb
    assert rq * (nb - na) < ra * (nb - nq) + rb * (nq - na)      # strictly below the line a-b


def test_a_compromise_plan_no_weighting_picks_is_found_with_its_proof():
    park = [Project("T", 4, 1, 6), Project("P", 4, 4, 4), Project("C", 5, 6, 1), Project("G", 3, 2, 2)]
    assert_proved(park, 10, unreachable(park, 10))


def test_none_when_every_unbeaten_plan_has_a_weighting():
    park = [Project("A", 7, 1, 10), Project("B", 8, 8, 6), Project("C", 9, 10, 1)]
    assert unreachable(park, 10) is None


def test_a_plan_that_spends_the_whole_budget_is_allowed():
    park = [Project("A", 7, 1, 10), Project("B", 8, 8, 6), Project("C", 9, 10, 1), Project("Q", 10, 4, 7)]
    assert_proved(park, 10, unreachable(park, 10))


def test_a_plan_on_the_line_between_two_others_counts_as_reachable():
    # M scores (50, 50), exactly halfway between A (0, 100) and B (100, 0): every unbeaten plan is supported
    park = [Project("A", 7, 0, 100), Project("M", 7, 50, 50), Project("B", 7, 100, 0)]
    assert unreachable(park, 10) is None


def test_the_proof_uses_plans_some_weighting_picks():
    # the two compromise plans are both unbeaten; the first lies above the line to the second
    park = [Project("A", 7, 0, 100), Project("Q1", 7, 20, 79), Project("Q2", 7, 50, 45), Project("B", 7, 100, 0)]
    assert_proved(park, 10, unreachable(park, 10))
