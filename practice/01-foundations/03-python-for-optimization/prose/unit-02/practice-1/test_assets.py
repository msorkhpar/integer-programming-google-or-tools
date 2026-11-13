from assets import parse_assets

# A pole and cable register unlike the lesson's portfolio: every cell arrives as text, as
# csv.DictReader gives it. Money in $k.
GOOD = {"asset_id": "C-104", "kind": "cable", "region": "East", "age": "41", "weibull_beta": "2.4",
        "weibull_eta": "55.5", "rul": "9", "cof": "1800"}
POLE = {"asset_id": "W-221", "kind": "pole", "region": "West", "age": "12", "weibull_beta": "3",
        "weibull_eta": "40", "rul": "25", "cof": "90"}


def with_bad(field: str, text: str) -> list[dict[str, str]]:
    """The good pole first, then the cable with one field replaced: the bad row is index 1."""
    return [POLE, {**GOOD, field: text}]


def test_valid_rows_become_typed_assets():
    assets, rejected = parse_assets([GOOD, POLE])
    assert rejected == []
    assert [a.asset_id for a in assets] == ["C-104", "W-221"]
    assert assets[0].age == 41 and isinstance(assets[0].age, int)
    assert assets[0].weibull_eta == 55.5 and assets[1].weibull_beta == 3.0
    assert assets[0].cof == 1800 and isinstance(assets[0].cof, int)


def test_a_negative_age_is_rejected():
    assets, rejected = parse_assets(with_bad("age", "-3"))
    assert rejected == [(1, "age")]
    assert [a.asset_id for a in assets] == ["W-221"]


def test_a_new_asset_of_age_zero_is_valid():
    assets, rejected = parse_assets(with_bad("age", "0"))
    assert rejected == [] and len(assets) == 2


def test_a_weibull_shape_of_zero_is_rejected():
    assert parse_assets(with_bad("weibull_beta", "0"))[1] == [(1, "weibull_beta")]


def test_a_blank_weibull_scale_is_rejected():
    assert parse_assets(with_bad("weibull_eta", ""))[1] == [(1, "weibull_eta")]


def test_a_cost_with_a_comma_is_rejected():
    assert parse_assets(with_bad("cof", "1,800"))[1] == [(1, "cof")]


def test_a_fractional_remaining_life_is_rejected():
    assert parse_assets(with_bad("rul", "2.5"))[1] == [(1, "rul")]


def test_a_region_outside_the_list_is_rejected():
    assert parse_assets(with_bad("region", "Central"))[1] == [(1, "region")]
