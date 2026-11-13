from renewal.fleet import KINDS, REGIONS, generate_fleet


def test_the_same_seed_gives_the_same_fleet():
    assert generate_fleet(200, seed=5) == generate_fleet(200, seed=5)
    assert generate_fleet(200, seed=5) != generate_fleet(200, seed=6)


def test_every_unit_has_values_in_range():
    fleet = generate_fleet(300)
    assert len(fleet) == 300
    assert len({t.tid for t in fleet}) == 300
    for t in fleet:
        assert t.kind in KINDS and t.region in REGIONS
        low, high = KINDS[t.kind].cost
        assert low <= t.cost <= high
        assert 0 <= t.condition <= 100
        assert 0 < t.pof < 1


def test_a_substation_sits_in_one_region():
    region = {}
    for t in generate_fleet(300):
        assert region.setdefault(t.substation, t.region) == t.region
