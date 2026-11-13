import itertools

from crew import build, solve

VALUES = [8.0, 5.0, 9.0, 3.0, 4.0, 11.0]                 # $k of avoided risk per job
HOURS = [[0, 2], [4, 0], [4, 1], [0, 0], [3, 3], [0, 1]]  # crew-weeks per job in quarters 1 and 2
CAPACITY = [8.0, 8.0]
REQUIRES = [(2, 3)]                                       # job 3 only if job 2


def best_by_hand():
    best = 0.0
    for plan in itertools.product((0, 1), repeat=len(VALUES)):
        fits = all(sum(HOURS[j][q] * plan[j] for j in range(len(VALUES))) <= CAPACITY[q] for q in range(2))
        if fits and all(plan[b] <= plan[a] for a, b in REQUIRES):
            best = max(best, sum(v * p for v, p in zip(VALUES, plan)))
    return best


def test_the_model_finds_the_best_selection():
    status, value, _ = solve(build(VALUES, HOURS, CAPACITY, REQUIRES))
    assert status == "Optimal" and abs(value - best_by_hand()) <= 1e-6


def test_a_rerun_on_one_thread_gives_the_same_bits():
    lp = build(VALUES, HOURS, CAPACITY, REQUIRES)
    first, second = solve(lp), solve(lp)
    assert first[0] == "Optimal" and first == second


def test_a_job_needs_the_job_it_depends_on():
    lp = build(VALUES, HOURS, CAPACITY, REQUIRES)
    assert solve(lp, {2: 1, 3: 1})[0] == "Optimal"
    assert solve(lp, {2: 0, 3: 1})[0] == "Infeasible"


def test_each_quarter_has_its_own_crew_limit():
    lp = build(VALUES, HOURS, CAPACITY, REQUIRES)
    assert solve(lp, {1: 1, 2: 1, 4: 0})[0] == "Optimal"
    assert solve(lp, {1: 1, 2: 1, 4: 1})[0] == "Infeasible"     # quarter 1: 4 + 4 + 3 = 11 > 8
