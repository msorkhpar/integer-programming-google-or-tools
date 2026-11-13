import pytest

from staffing import legacy_plan, mathopt_plan

#: kind -> (hours a crew covers, cost of a crew, most crews, union minimum)
BASE = {"line": (40, 30, 6, 1), "tree": (30, 20, 6, 0), "contract": (50, 45, 4, 0)}


def depot(**changes):
    data = {"crews": dict(BASE), "need_low": 200, "need_high": 240, "overtime_max": 40, "overtime_rate": 0.5}
    data.update(changes)
    return data


def agree(data):
    old_status, old_cost, old_plan = legacy_plan(data)
    new_status, new_cost, new_plan = mathopt_plan(data)
    assert new_status == old_status
    if old_cost is None:
        assert new_cost is None
    else:
        assert new_cost == pytest.approx(old_cost, abs=1e-6)
        assert set(new_plan) == set(old_plan)


def test_the_port_gives_the_legacy_cost_on_the_base_depot():
    agree(depot())
    assert mathopt_plan(depot())[1] == pytest.approx(130)


def test_overtime_is_never_negative():
    agree(depot(overtime_rate=2.0))          # overtime dearer than every crew hour


def test_crews_come_in_whole_numbers():
    agree(depot(need_low=205))               # 4 1/6 tree crews would be cheaper


def test_the_union_minimum_is_kept():
    crews = dict(BASE, contract=(50, 45, 4, 1))
    agree(depot(crews=crews))


def test_the_cover_row_keeps_its_upper_bound():
    crews = dict(BASE, line=(40, 30, 6, 4), tree=(30, 20, 6, 1))   # minimums alone cover 190 hours
    agree(depot(crews=crews, need_low=150, need_high=170))
    assert mathopt_plan(depot(crews=crews, need_low=150, need_high=170))[0] == "INFEASIBLE"
