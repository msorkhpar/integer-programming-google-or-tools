from ortools.math_opt.python import mathopt

from dock import add_dock_row, choice_variables, dock_m

ORDERS = {"O1": {"small": 4, "big": 9, "rail": 0}, "O2": {"small": 3, "big": 7}, "O3": {"van": 2, "big": 5}}
CAPACITY = 14


def allowed(plan: dict[str, str], overflow: int) -> bool:
    model = mathopt.Model()
    choose = choice_variables(model, ORDERS)
    yard = model.add_binary_variable(name="overflow")
    add_dock_row(model, choose, ORDERS, CAPACITY, yard)
    for (o, opt), var in choose.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(o) == opt else 0.0
    yard.lower_bound = yard.upper_bound = overflow
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_load_over_capacity_needs_the_overflow_yard():
    assert allowed({"O1": "small", "O2": "big"}, overflow=0) is True       # 11 pallets
    assert allowed({"O1": "big", "O2": "big"}, overflow=0) is False        # 16 pallets


def test_the_overflow_yard_takes_the_heaviest_plan():
    heaviest = {"O1": "big", "O2": "big", "O3": "big"}                   # 21 pallets
    assert allowed(heaviest, overflow=1) is True
    assert allowed(heaviest, overflow=0) is False


def test_each_order_counts_only_its_heaviest_option():
    assert dock_m(ORDERS, CAPACITY) == 7


def test_m_is_zero_when_the_dock_can_never_overflow():
    assert dock_m(ORDERS, 30) == 0
    assert dock_m(ORDERS, CAPACITY) == 7
