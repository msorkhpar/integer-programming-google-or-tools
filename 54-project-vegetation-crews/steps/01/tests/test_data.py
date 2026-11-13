"""The generated seasons and the loader."""

from vegcrew.data import season_from_dict
from vegcrew.generate import SIZES, scenario


def test_the_same_seed_gives_the_same_season():
    assert scenario("small", 54) == scenario("small", 54)
    assert scenario("small", 54) != scenario("small", 55)


def test_every_size_has_its_number_of_circuits_and_positive_numbers():
    for size, n in SIZES.items():
        season = season_from_dict(scenario(size))
        assert len(season.circuits) == n
        assert all(c.miles > 0 and c.cost > 0 and c.risk > 0 for c in season.circuits)
        assert 0 < season.budget < sum(c.cost for c in season.circuits)


def test_the_loader_ignores_columns_it_does_not_use():
    raw = {"budget": 10, "circuits": [{"id": "A", "region": "North", "miles": 5, "cost": 9, "risk": 3,
                                       "soil": "clay"}]}
    season = season_from_dict(raw)
    assert season.circuit("A").cost == 9
    assert season.name == "season"
