from xproute import xpress_license

MOUNTED = {"/run/secrets/xpress/xpauth.xpr", "/app/main.py"}


def test_a_mounted_license_file_is_found_and_none_means_community():
    assert xpress_license({"XPRESS": "/run/secrets/xpress"}, MOUNTED) == "license file /run/secrets/xpress/xpauth.xpr"
    assert xpress_license({"PATH": "/usr/bin"}, MOUNTED) == "community license"


def test_xpress_naming_the_file_itself_is_caught():
    got = xpress_license({"XPRESS": "/run/secrets/xpress/xpauth.xpr"}, MOUNTED)
    assert got == "XPRESS names the file; set it to the folder that holds xpauth.xpr"


def test_a_folder_without_the_file_is_reported():
    assert xpress_license({"XPRESS": "/run/secrets/xpress"}, MOUNTED) == "license file /run/secrets/xpress/xpauth.xpr"
    assert xpress_license({"XPRESS": "/opt/xpress"}, MOUNTED) == "no xpauth.xpr in /opt/xpress"


def test_a_trailing_slash_on_the_folder_still_finds_the_file():
    assert xpress_license({"XPRESS": "/run/secrets/xpress/"}, MOUNTED) == "license file /run/secrets/xpress/xpauth.xpr"


def test_an_empty_setting_counts_as_unset():
    assert xpress_license({"XPRESS": ""}, MOUNTED) == "community license"
