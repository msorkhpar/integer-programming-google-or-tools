from ortools.sat.python import cp_model

from release import add_rules

# A software team's candidate features for one release, not the lesson's portfolio.
FEATURES = ["sso", "audit", "export", "pdf", "csv", "dark", "themes", "mobile", "push"]
REQUIRES = [("audit", "sso")]                     # the audit log needs single sign-on
EXCLUDES = [("dark", "themes")]                   # one UI rework per release
NEEDS_ONE_OF = [("export", ["pdf", "csv"])]       # export needs at least one format
BUNDLES = [("mobile", "push")]                    # the app and its notifications ship together


def allowed(plan: set[str]) -> bool:
    """Fix which features ship and ask CP-SAT whether every rule holds."""
    model = cp_model.CpModel()
    x = {f: model.new_bool_var(f) for f in FEATURES}
    add_rules(model, x, REQUIRES, EXCLUDES, NEEDS_ONE_OF, BUNDLES)
    for f, var in x.items():
        model.add(var == (1 if f in plan else 0))
    return cp_model.CpSolver().solve(model) == cp_model.OPTIMAL


def test_a_required_feature_must_ship_too():
    assert allowed({"audit", "sso"}) is True
    assert allowed({"audit"}) is False


def test_excluded_features_never_ship_together():
    assert allowed({"dark"}) is True
    assert allowed({"dark", "themes"}) is False


def test_a_feature_that_needs_one_of_several_gets_one():
    assert allowed({"export", "csv"}) is True
    assert allowed({"export"}) is False


def test_a_bundle_ships_whole():
    assert allowed({"mobile", "push"}) is True
    assert allowed({"mobile"}) is False
    assert allowed({"push"}) is False


def test_a_requirement_works_one_way_only():
    # sso without the audit log is fine: the rule is about what audit needs.
    assert allowed({"sso"}) is True
    assert allowed({"audit", "csv"}) is False


def test_more_than_one_of_the_options_is_fine():
    assert allowed({"export", "pdf", "csv"}) is True
    assert allowed({"export", "sso"}) is False
