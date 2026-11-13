import pytest

from sweep import sweep

PLANS = [(5200, 300.0), (4800, 420.0), (4500, 470.0), (4100, 510.0)]     # (riders, tonnes cut)


class Model:
    """Stands in for the agency's model: the most riders among plans that cut at least the floor."""

    def __init__(self, plans=PLANS):
        self.plans, self.asked = plans, []

    def __call__(self, floor):
        self.asked.append(floor)
        meeting = [p for p in self.plans if p[1] >= floor - 1e-9]
        return max(meeting) if meeting else None


def test_three_floors_give_three_plans_in_floor_order():
    plans = [(5200, 300.0), (4800, 400.0), (4100, 500.0)]
    assert sweep(Model(plans), 300, 500, 3) == plans


def test_the_floors_run_from_low_to_high_inclusive():
    model = Model()
    sweep(model, 300, 510, 4)
    assert model.asked == pytest.approx([300, 370, 440, 510])


def test_a_plan_found_twice_is_listed_once():
    assert sweep(Model(), 300, 510, 8) == PLANS


def test_a_floor_no_plan_reaches_adds_nothing():
    assert sweep(Model(), 400, 600, 3) == [(4800, 420.0), (4100, 510.0)]
