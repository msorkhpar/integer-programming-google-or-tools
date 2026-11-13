import depot_rules
from depot_rules import Rule, feasible, minimal_clash

# A utility's outage-week crew rules, not the lesson's portfolio.
CREWS = {"north": (0, 6), "south": (0, 6), "east": (0, 6)}
TOTAL = Rule("total_cap", {"north": 1, "south": 1, "east": 1}, "<=", 15)
NORTH_MAX = Rule("north_max", {"north": 1}, "<=", 3)
NORTH_MIN = Rule("north_min", {"north": 1}, ">=", 5)
SOUTH_MAX = Rule("south_max", {"south": 1}, "<=", 1)
SOUTH_MIN = Rule("south_min", {"south": 1}, ">=", 4)
PAIR = Rule("pair_min", {"north": 1, "east": 1}, ">=", 4)


def check_minimal(rules, clash):
    by_name = {r.name: r for r in rules}
    assert clash, "an infeasible scenario has a clash"
    assert not feasible(CREWS, [by_name[n] for n in clash]), "the clash must be infeasible on its own"
    for name in clash:
        rest = [by_name[n] for n in clash if n != name]
        assert feasible(CREWS, rest), f"{name} can be dropped and the rest still clash"


def test_one_clash_among_harmless_rules_is_found_exactly():
    rules = [TOTAL, PAIR, NORTH_MAX, NORTH_MIN]
    clash = minimal_clash(CREWS, rules)
    check_minimal(rules, clash)
    assert sorted(clash) == ["north_max", "north_min"]


def test_a_scenario_that_can_be_met_has_no_clash():
    assert minimal_clash(CREWS, [TOTAL, PAIR, NORTH_MAX]) == []
    assert minimal_clash(CREWS, [TOTAL, NORTH_MAX, NORTH_MIN]) == ["north_max", "north_min"]


def test_when_every_rule_is_named_one_whole_clash_comes_back(monkeypatch):
    # CP-SAT may name every assumed rule as sufficient (lesson 4.6.2 shows it on GridCap).
    monkeypatch.setattr(depot_rules, "clashing_rules", lambda variables, rules: sorted(r.name for r in rules))
    rules = [TOTAL, NORTH_MAX, NORTH_MIN, SOUTH_MAX, SOUTH_MIN]
    clash = minimal_clash(CREWS, rules)
    check_minimal(rules, clash)
    assert sorted(clash) in (["north_max", "north_min"], ["south_max", "south_min"])
