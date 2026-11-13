from masking import mask_line


def test_user_and_host_are_replaced():
    line = "License check failed (user mira, host plan-07, cores 8)"
    assert mask_line(line) == "License check failed (user <user>, host <host>, cores 8)"


def test_a_line_with_nothing_personal_is_unchanged():
    line = "Model too large: 2,412 variables, limit 2,000"
    assert mask_line(line) == line


def test_an_empty_user_is_still_masked():
    line = "No license found (user , host box1, hostid 7f)"
    assert mask_line(line) == "No license found (user <user>, host <host>, hostid 7f)"


def test_email_addresses_are_replaced():
    line = "License issued to dana.ops+grb@depot-net.example.org; renew soon"
    assert mask_line(line) == "License issued to <email>; renew soon"


def test_access_keys_are_replaced():
    line = "token request for 3f2a9c1e-77b4-4d0a-9e21-5c8d0b6a1f47 refused"
    assert mask_line(line) == "token request for <key> refused"
