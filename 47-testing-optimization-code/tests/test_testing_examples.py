"""The module 47 examples: one-rule tests, Hypothesis properties, the golden file, determinism, back-tests."""

import pytest
from gridcap import generate

import golden
from backtest import backtest
from blind_spot import whole_model_test
from bugs import BUGS, broken
from determinism import digests
from history import CYCLES
from one_rule import outcome
from plan_model import RULES
from properties import PROPERTIES, never_worse_than_the_witness, plan_obeys_every_rule, property_test
from rule_tests import TESTS


@pytest.mark.parametrize("test", TESTS, ids=lambda t: t.__name__)
def test_every_one_rule_test_passes_on_the_real_rules(test):
    assert outcome(test, RULES) is None


@pytest.mark.parametrize("bug", list(BUGS))
def test_every_bug_fails_some_one_rule_test(bug):
    assert any(outcome(test, broken(bug)) for test in TESTS)


def test_the_whole_model_test_misses_the_too_strict_lag_on_small():
    assert whole_model_test(generate("small"), broken("precedence adds 1 to the lag"))[2] == "PASS"
    assert whole_model_test(generate("small"), broken("precedence ignores the lag"))[2] == "FAIL"


@pytest.mark.parametrize("check", PROPERTIES, ids=lambda c: c.__name__)
def test_every_property_holds_on_the_real_rules(check):
    property_test(check)()


@pytest.mark.parametrize("bug", [b for b in BUGS if b != "precedence adds 1 to the lag"])
def test_validity_catches_every_bug_that_loosens_a_rule(bug):
    with pytest.raises(AssertionError):
        property_test(plan_obeys_every_rule, broken(bug), pinned=False)()


def test_only_the_witness_catches_the_too_strict_lag():
    rules = broken("precedence adds 1 to the lag")
    property_test(plan_obeys_every_rule, rules, pinned=False)()
    with pytest.raises(AssertionError):
        property_test(never_worse_than_the_witness, rules, pinned=False)()


def test_the_current_model_matches_the_golden_file():
    stored = golden.load()
    for name, portfolio in golden.scenarios().items():
        assert golden.compare(stored[name], golden.result(portfolio)) == [], name


def test_compare_names_a_tie_and_ignores_noise():
    base = {"input_sha256": "h", "status": "OPTIMAL", "objective": 30.0, "plan": {"A": 2027}, "spend": {"2027": 50}}
    assert golden.compare(base, {**base, "objective": 30.00001}) == []
    tie = golden.compare(base, {**base, "plan": {"B": 2027}})
    assert tie[-1].startswith("same value, another plan")
    assert golden.compare(base, {**base, "input_sha256": "g"})[0].startswith("input changed")


def test_a_fresh_process_repeats_and_set_order_does_not():
    assert len(set(digests("small", runs=3))) == 1
    assert len(set(digests("two equal projects, room for one", order="set", runs=5))) == 2


@pytest.mark.parametrize("cycle", CYCLES)
def test_backtest_todays_plans_are_valid_and_the_old_ones_overspend(cycle):
    result = backtest(cycle)
    assert result["status"] == "OPTIMAL" and result["now_breaks"] == []
    assert result["then_breaks"] and all("over the budget" in line for line in result["then_breaks"])
