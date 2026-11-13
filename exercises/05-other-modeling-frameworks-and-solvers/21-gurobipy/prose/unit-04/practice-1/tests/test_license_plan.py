from license_plan import license_plan

KEY = {"WLSACCESSID": "aaaa-1111", "WLSSECRET": "bbbb-2222", "LICENSEID": "424242"}


def only(*paths):
    return lambda path: path in paths


def test_a_complete_wls_key_is_used():
    kind, params = license_plan(dict(KEY), only())
    assert kind == "wls"
    assert params == {"WLSACCESSID": "aaaa-1111", "WLSSECRET": "bbbb-2222", "LICENSEID": 424242}


def test_a_named_license_file_is_used():
    environ = {"GRB_LICENSE_FILE": "/run/secrets/grb.lic", "HOME": "/srv/jobs"}
    assert license_plan(environ, only("/run/secrets/grb.lic")) == ("file", "/run/secrets/grb.lic")


def test_a_missing_named_file_is_not_replaced_by_a_default():
    environ = {"GRB_LICENSE_FILE": "/run/secrets/grb.lic", "HOME": "/srv/jobs"}
    assert license_plan(environ, only("/opt/gurobi/gurobi.lic")) == (
        "error", "license file not found: /run/secrets/grb.lic")


def test_the_default_places_are_searched_in_order():
    environ = {"HOME": "/srv/jobs"}
    both = only("/opt/gurobi/gurobi.lic", "/srv/jobs/gurobi.lic")
    assert license_plan(environ, both) == ("file", "/opt/gurobi/gurobi.lic")
    assert license_plan(environ, only("/srv/jobs/gurobi.lic")) == ("file", "/srv/jobs/gurobi.lic")
    assert license_plan({}, only("/srv/jobs/gurobi.lic")) == ("error", "no license")


def test_half_a_wls_key_is_an_error_naming_what_is_missing():
    kind, message = license_plan({"WLSACCESSID": "aaaa-1111"}, only())
    assert (kind, message) == ("error", "incomplete WLS key: WLSSECRET, LICENSEID not set")
    kind, message = license_plan({"WLSACCESSID": "aaaa-1111", "LICENSEID": "424242"}, only("/opt/gurobi/gurobi.lic"))
    assert (kind, message) == ("error", "incomplete WLS key: WLSSECRET not set")
