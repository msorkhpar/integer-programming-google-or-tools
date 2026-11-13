from ortools.math_opt.python import mathopt

from crew_cases import YEARS, cases


def months_in(jobs, x, year):
    """Crew-months the started jobs use in `year`: job j started in s uses months[k] in s + k."""
    total = mathopt.LinearExpression()
    for job, (months, first, last) in jobs.items():
        for s in range(first, last + 1):
            if 0 <= year - s < len(months):
                total += months[year - s] * x[job, s]
    return total


def crew_rule(model, x, jobs, crews):
    for y in YEARS:
        model.add_linear_constraint(months_in(jobs, x, y) <= crews[y], name=f"crews_{y}")


def one_month_short(model, x, jobs, crews):
    """Written as if the limit were strict: `<` turned into `<= crews - 1`."""
    for y in YEARS:
        model.add_linear_constraint(months_in(jobs, x, y) <= crews[y] - 1, name=f"crews_{y}")


def skips_last_year(model, x, jobs, crews):
    for y in YEARS[:-1]:
        model.add_linear_constraint(months_in(jobs, x, y) <= crews[y], name=f"crews_{y}")


def charges_start_year(model, x, jobs, crews):
    """Every month of a job charged to the year it starts."""
    for y in YEARS:
        total = mathopt.LinearExpression()
        for job, (months, first, last) in jobs.items():
            if first <= y <= last:
                total += sum(months) * x[job, y]
        model.add_linear_constraint(total <= crews[y], name=f"crews_{y}")


def verdict(rule, jobs, crews, plan):
    """Does a model with this crew rule (and nothing else) accept the plan?"""
    model = mathopt.Model()
    x = {(job, s): model.add_binary_variable(name=f"x_{job}_{s}")
         for job, (months, first, last) in jobs.items() for s in range(first, last + 1)}
    rule(model, x, jobs, crews)
    if any((job, s) not in x for job, s in plan.items()):
        return False
    for (job, s), var in x.items():
        value = 1.0 if plan.get(job) == s else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def caught(rule):
    """Some case whose verdict under `rule` differs from the one the case states."""
    return any(verdict(rule, jobs, crews, plan) != expected for jobs, crews, plan, expected in cases())


def test_every_verdict_matches_the_rule_and_both_kinds_appear():
    found = cases()
    assert any(expected for *_, expected in found)
    assert any(not expected for *_, expected in found)
    for jobs, crews, plan, expected in found:
        assert verdict(crew_rule, jobs, crews, plan) == expected, plan


def test_a_case_catches_a_rule_that_refuses_a_full_year():
    assert caught(one_month_short)


def test_a_case_catches_a_rule_that_skips_the_last_year():
    assert caught(skips_last_year)


def test_a_case_catches_a_rule_that_charges_the_start_year():
    assert caught(charges_start_year)
