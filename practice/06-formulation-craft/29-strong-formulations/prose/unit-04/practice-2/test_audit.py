from ortools.math_opt.python import mathopt

from audit import audit

# Three formulations of "pick at most one of three tools" (not the lesson's model); the best is 5.


def variant(rows):
    def build(integer):
        model = mathopt.Model()
        a, b, c = (model.add_variable(lb=0, ub=1, is_integer=integer, name=n) for n in "abc")
        for row in rows:
            model.add_linear_constraint(row(a, b, c))
        model.maximize(5 * a + 4 * b + 3 * c)
        return model
    return build


VARIANTS = {
    "inherited": variant([lambda a, b, c: 3 * a + 3 * b + 3 * c <= 5]),
    "one pair added": variant([lambda a, b, c: 3 * a + 3 * b + 3 * c <= 5, lambda a, b, c: a + b <= 1]),
    "one row": variant([lambda a, b, c: a + b + c <= 1]),
}


def test_each_formulation_gets_its_line_in_order():
    lines = audit(VARIANTS, optimum=5)
    assert [line["name"] for line in lines] == ["inherited", "one pair added", "one row"]
    assert [(line["variables"], line["rows"]) for line in lines] == [(3, 1), (3, 2), (3, 1)]
    assert [round(line["lp"], 3) for line in lines] == [7.667, 7.0, 5.0]


def test_the_share_closed_is_measured_against_the_inherited_gap():
    lines = audit(VARIANTS, optimum=5)
    # Inherited gap 7.667 - 5 = 2.667; one pair closes 0.667 of it, a quarter; one row all of it.
    assert [round(line["closed"], 3) for line in lines] == [0.0, 0.25, 1.0]


def test_the_root_bound_is_the_solvers_after_its_root_node():
    lines = audit(VARIANTS, optimum=5)
    assert lines, "one line per formulation"
    inherited = lines[0]
    assert 5 - 1e-6 <= inherited["root"] < inherited["lp"] - 0.5


def test_an_inherited_model_with_no_gap_reports_it_closed():
    lines = audit({"one row": VARIANTS["one row"]}, optimum=5)       # its LP bound is the optimum, 5
    assert [round(line["closed"], 3) for line in lines] == [1.0]
