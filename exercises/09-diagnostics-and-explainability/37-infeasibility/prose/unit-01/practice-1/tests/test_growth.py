import math

from ortools.math_opt.python import mathopt

from growth import free_to_grow

INF = math.inf


def test_an_unbounded_rewarded_variable_in_no_row_is_named_and_a_bounded_one_is_not():
    m = mathopt.Model()
    beds = m.add_variable(lb=0, ub=40, name="beds")
    rebate = m.add_variable(lb=0, name="rebate")
    m.maximize(3 * beds + 1 * rebate)
    assert free_to_grow(m) == ["rebate"]
    rebate.upper_bound = 1000
    assert free_to_grow(m) == []


def test_a_row_only_limits_the_direction_its_bound_faces():
    m = mathopt.Model()
    stock = m.add_variable(lb=0, name="stock")
    used = m.add_variable(lb=0, ub=10, name="used")
    m.add_linear_constraint(used - stock <= 0, name="use_what_you_have")    # stock may grow freely
    m.maximize(stock)
    assert free_to_grow(m) == ["stock"]
    m.add_linear_constraint(stock - used <= 50, name="shelf_space")         # now it may not
    assert free_to_grow(m) == []


def test_a_minimization_pushes_variables_the_other_way():
    m = mathopt.Model()
    credit = m.add_variable(lb=0, name="credit")
    fee = m.add_variable(lb=0, name="fee")
    m.minimize(5 * fee - 2 * credit)
    assert free_to_grow(m) == ["credit"]


def test_a_variable_can_run_away_downward():
    m = mathopt.Model()
    balance = m.add_variable(lb=-INF, ub=100, name="balance")
    floor = m.add_variable(lb=-INF, ub=0, name="floor")
    m.add_linear_constraint(floor >= -20, name="overdraft_limit")
    m.maximize(-1 * balance - 1 * floor)
    assert free_to_grow(m) == ["balance"]
