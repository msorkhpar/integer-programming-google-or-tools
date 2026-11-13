from hypothesis import Phase, given, settings

from drawn_properties import check, holds, portfolios

FIND = (Phase.explicit, Phase.reuse, Phase.generate)      # no shrinking: the tests only ask "caught or not"


def survives(skip: frozenset = frozenset(), examples: int = 200) -> bool:
    """True if every property holds on `examples` drawn portfolios for the model with `skip` planted."""
    @settings(max_examples=examples, derandomize=True, database=None, deadline=None, phases=FIND)
    @given(portfolios())
    def run(case):
        holds(*case, skip=skip)
    try:
        run()
    except AssertionError:
        return False
    return True


def test_every_property_holds_on_200_drawn_portfolios_and_a_model_without_budgets_fails():
    assert survives()
    assert not survives(frozenset({"budget"}))


def test_every_witness_breaks_no_rule():
    found, witnesses = [], []

    @settings(max_examples=200, derandomize=True, database=None, deadline=None, phases=FIND)
    @given(portfolios())
    def run(case):
        snapshot, witness = case
        found.append(check(snapshot, witness))
        witnesses.append(witness)
    run()
    assert found and all(broken == [] for broken in found)
    assert len(witnesses) > 100 and any(w for w in witnesses)


def test_a_model_without_alternative_rows_is_caught():
    assert not survives(frozenset({"alt"}))


def test_a_model_that_reads_every_lag_as_zero_is_caught():
    assert not survives(frozenset({"lag"}))


def test_a_model_without_must_do_rows_is_caught():
    assert not survives(frozenset({"must"}))


def test_a_model_that_reports_a_value_its_plan_does_not_have_is_caught():
    assert not survives(frozenset({"value"}))
