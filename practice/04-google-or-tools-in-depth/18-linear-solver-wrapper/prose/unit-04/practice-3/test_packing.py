from packing import fewest_crews


def valid(sizes, season, result, count):
    assert result is not None
    used, packing = result
    assert used == count
    assert sorted(i for p in packing for i in p) == list(range(len(sizes)))
    assert all(sum(sizes[i] for i in p) <= season for p in packing)


def test_jobs_are_packed_into_the_fewest_seasons():
    valid([3, 3, 2, 2, 2, 2], 7, fewest_crews([3, 3, 2, 2, 2, 2], 7), 2)


def test_only_used_seasons_are_listed():
    result = fewest_crews([5, 4, 3], 12)
    valid([5, 4, 3], 12, result, 1)
    assert result[1] == [[0, 1, 2]]


def test_enough_seasons_are_offered_when_the_total_misleads():
    valid([6, 6, 6], 10, fewest_crews([6, 6, 6], 10), 3)     # 18 months, yet no two jobs share a season


def test_a_job_longer_than_a_season_gives_no_packing():
    assert fewest_crews([4, 13, 2], 12) is None
