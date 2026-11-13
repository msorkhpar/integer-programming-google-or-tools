from screen import screen

TABLE = {
    "Alder": {"refuses": {"semicontinuous", "quadratic"}, "alters": set()},
    "Birch": {"refuses": set(), "alters": set()},
    "Cedar": {"refuses": set(), "alters": {"continuous"}},
    "Damson": {"refuses": {"indicator"}, "alters": {"continuous"}},
}


def test_a_refused_feature_rules_a_solver_out():
    verdicts = screen({"quadratic"}, TABLE)
    assert verdicts["Alder"] == "refuses quadratic"
    assert verdicts["Birch"] == "ok"


def test_a_quiet_change_rules_a_solver_out_too():
    assert screen({"quadratic"}, TABLE)["Alder"] == "refuses quadratic"
    assert screen({"continuous"}, TABLE)["Cedar"] == "alters continuous"


def test_a_refusal_is_reported_before_a_quiet_change():
    assert screen({"continuous", "indicator"}, TABLE)["Damson"] == "refuses indicator"


def test_the_first_problem_in_alphabetical_order_is_named():
    assert screen({"semicontinuous", "quadratic"}, TABLE)["Alder"] == "refuses quadratic"


def test_features_the_model_does_not_use_do_not_matter():
    verdicts = screen({"binary", "quadratic"}, TABLE)
    assert verdicts == {"Alder": "refuses quadratic", "Birch": "ok", "Cedar": "ok", "Damson": "ok"}
