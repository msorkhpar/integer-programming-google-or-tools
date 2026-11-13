import pyomo.environ as pyo

from iis import deletion_filter

# Small staffing models, not the lesson's portfolio.


def staffing():
    m = pyo.ConcreteModel()
    m.day = pyo.Var(bounds=(0, 8))
    m.night = pyo.Var(bounds=(0, 8))
    m.cover = pyo.Constraint(expr=m.day + m.night >= 14)
    m.union = pyo.Constraint(expr=m.night <= 4)
    m.budget = pyo.Constraint(expr=3 * m.day + 4 * m.night <= 60)
    m.mix = pyo.Constraint(expr=m.day - m.night <= 6)
    m.cost = pyo.Objective(expr=3 * m.day + 4 * m.night)
    return m


def run(m):
    try:
        return deletion_filter(m)
    except Exception as error:
        raise AssertionError(f"deletion_filter raised {type(error).__name__}: {error}") from None


def test_one_conflict_between_cover_and_the_union_cap():
    assert run(staffing()) == ["cover", "union"]


def test_three_rows_where_any_two_agree():
    m = pyo.ConcreteModel()
    m.x = pyo.Var(bounds=(0, 10))
    m.y = pyo.Var(bounds=(0, 10))
    m.p = pyo.Constraint(expr=m.x + m.y >= 9)
    m.q = pyo.Constraint(expr=m.x - m.y >= 5)
    m.r = pyo.Constraint(expr=m.x <= 6)
    m.s = pyo.Constraint(expr=m.y <= 9)
    assert run(m) == ["p", "q", "r"]


def test_two_separate_conflicts_give_one_of_them():
    m = staffing()
    m.van = pyo.Var(bounds=(0, 3))
    m.trips = pyo.Constraint(expr=m.van >= 5)
    found = run(m)
    assert found in (["cover", "union"], ["trips"]), f"got {found}"
