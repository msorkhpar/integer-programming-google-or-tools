from chooser import Problem, choose_api


def test_routes_go_to_routing():
    assert choose_api(Problem(routes=True)) == "routing"


def test_exact_shapes_go_to_their_special_solvers():
    assert choose_api(Problem(shape="assignment")) == "graph"
    assert choose_api(Problem(shape="flow")) == "graph"
    assert choose_api(Problem(shape="knapsack")) == "knapsack"


def test_fractions_and_duals_go_to_mathopt():
    assert choose_api(Problem(continuous=True)) == "MathOpt"
    assert choose_api(Problem(needs_duals=True)) == "MathOpt"


def test_intervals_and_logic_go_to_cp_sat():
    assert choose_api(Problem(intervals=True)) == "CP-SAT"
    assert choose_api(Problem(logic=True)) == "CP-SAT"


def test_a_plain_integer_model_goes_to_mathopt():
    assert choose_api(Problem()) == "MathOpt"


def test_one_rule_outside_the_shape_makes_it_general():
    assert choose_api(Problem(shape="assignment", side_rules=True)) == "MathOpt"
    assert choose_api(Problem(shape="knapsack", side_rules=True, logic=True)) == "CP-SAT"
    assert choose_api(Problem(shape="flow", side_rules=True, continuous=True)) == "MathOpt"


def test_routes_stay_with_routing_when_rules_pile_on():
    assert choose_api(Problem(routes=True, side_rules=True, intervals=True)) == "routing"
    assert choose_api(Problem(routes=True, continuous=True, logic=True)) == "routing"


def test_logic_with_fractions_goes_to_mathopt():
    assert choose_api(Problem(logic=True, continuous=True)) == "MathOpt"
    assert choose_api(Problem(intervals=True, needs_duals=True)) == "MathOpt"
