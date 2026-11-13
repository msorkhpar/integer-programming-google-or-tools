import pytest

import sweep as module
from sweep import sweep

# A water utility's pipe renewals: name -> (cost $k, value $k). Not the lesson's portfolio.
PIPES = {"R1": (40, 62), "R2": (30, 41), "R3": (25, 30), "R4": (20, 27), "R5": (15, 16)}


def run(projects, budgets):
    try:
        return sweep(projects, budgets)
    except Exception as error:
        raise AssertionError(f"sweep raised {type(error).__name__}: {error}") from None


def test_each_budget_gets_its_own_optimum():
    assert run(PIPES, [20, 50, 75, 130]) == pytest.approx([27, 68, 105, 176])


def test_a_budget_that_falls_after_rising_is_still_right():
    assert run(PIPES, [90, 45, 60]) == pytest.approx([130, 62, 89])


def test_the_model_is_built_once_for_the_whole_sweep(monkeypatch):
    calls = []
    real = module.build

    def counted(*args, **kwargs):
        calls.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(module, "build", counted)
    values = run(PIPES, [20, 50, 75, 130])
    assert len(calls) == 1, f"build was called {len(calls)} times for 4 budgets"
    assert values == pytest.approx([27, 68, 105, 176])
