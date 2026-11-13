from itertools import product

from crew_rules import Rule, clashing_rules

# A utility's outage-week crew rules, not the lesson's portfolio.
CREWS = {"north": (2, 6), "south": (1, 6), "east": (0, 6)}
TOTAL = Rule("total_cap", {"north": 1, "south": 1, "east": 1}, "<=", 10)
PAIR = Rule("north_south_cap", {"north": 1, "south": 1}, "<=", 2)
EAST = Rule("east_min", {"east": 1}, ">=", 1)


def holds(rule, point):
    total = sum(coef * point[name] for name, coef in rule.terms.items())
    return total <= rule.rhs if rule.sense == "<=" else total >= rule.rhs


def feasible(variables, rules):
    names = list(variables)
    for values in product(*(range(lo, hi + 1) for lo, hi in variables.values())):
        point = dict(zip(names, values))
        if all(holds(r, point) for r in rules):
            return True
    return False


def check_clash(variables, rules, clash):
    by_name = {r.name: r for r in rules}
    assert clash, "an infeasible scenario names at least one rule"
    assert set(clash) <= set(by_name)
    assert not feasible(variables, [by_name[n] for n in clash]), "the named rules must clash on their own"


def test_a_clash_with_the_crews_domains_is_named():
    rules = [TOTAL, PAIR, EAST]
    check_clash(CREWS, rules, clashing_rules(CREWS, rules))
    assert "north_south_cap" in clashing_rules(CREWS, rules)


def test_a_scenario_that_can_be_met_names_nothing():
    assert clashing_rules(CREWS, [TOTAL, EAST]) == []
    assert clashing_rules(CREWS, [TOTAL, PAIR, EAST]) != []


def test_a_clash_between_a_minimum_and_a_maximum_names_both():
    rules = [TOTAL, Rule("north_max", {"north": 1}, "<=", 3), Rule("north_min", {"north": 1}, ">=", 5)]
    clash = clashing_rules(CREWS, rules)
    check_clash(CREWS, rules, clash)
    assert {"north_max", "north_min"} <= set(clash)
