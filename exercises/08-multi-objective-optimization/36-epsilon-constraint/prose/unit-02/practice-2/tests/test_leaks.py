from leaks import exact_sweep

FRONTIER = [(870.0, 100), (880.0, 103), (900.0, 112), (930.0, 113), (950.0, 130)]   # (leak cut, cost)


class Model:
    """The most leak cut among plans costing at most the ceiling, with the slack; counts its calls."""

    def __init__(self, frontier=FRONTIER):
        self.frontier, self.calls = frontier, 0

    def __call__(self, ceiling):
        self.calls += 1
        within = [p for p in self.frontier if p[1] <= ceiling]
        if not within:
            return None
        best = max(within)
        return best, ceiling - best[1]


def test_every_plan_is_found_in_order():
    assert exact_sweep(Model(), 90, 130) == FRONTIER[::-1]


def test_one_solve_per_plan_when_the_bottom_is_reached():
    model = Model()
    assert exact_sweep(model, 100, 130) == FRONTIER[::-1]
    assert model.calls == 5


def test_the_first_ceiling_no_plan_meets_ends_the_sweep():
    model = Model()
    assert exact_sweep(model, 50, 130) == FRONTIER[::-1]
    assert model.calls == 6


def test_the_jump_counts_in_steps():
    frontier = [(870.0, 100), (900.0, 140), (930.0, 150), (950.0, 200)]
    model = Model(frontier)
    assert exact_sweep(model, 100, 200, step=5) == frontier[::-1]
    assert model.calls == 4


def test_a_top_that_is_not_a_multiple_of_the_step():
    frontier = [(870.0, 100), (900.0, 140), (930.0, 150), (940.0, 195), (950.0, 200)]
    model = Model(frontier)
    assert exact_sweep(model, 100, 203, step=5) == frontier[::-1]
    assert model.calls == 5
