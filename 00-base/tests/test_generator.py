"""GridCap's generator: deterministic, structurally sound, and the same bytes everywhere."""

from __future__ import annotations

import pytest

from gridcap import PROGRAMS, REGIONS, SIZES, Portfolio, generate, load_csv, save_csv

#: The content hash of each size at the default seed. A change here changes every lesson's output,
#: so it must be deliberate: regenerate the outputs the lessons quote in the same commit.
PINNED = {
    "tiny": "906823083dc6a31e63d089baa0655882ffd6b1a12ccf94f4b0f5ba429b0f78f8",
    "small": "29d5349c5b5ab600ecfb86b6d3c1fbe3cd0adaa21f7abfec385b4d3387a195e7",
    "medium": "df4edafe8608cd32dac97f26d0ad53e7a1e202fbb10fa232bce92bd5f3132c7a",
    "large": "092cac4f6f56f699439d198d829a459f557c8f05e8844029dcce1878dd99d593",
}
COUNTS = {"tiny": 8, "small": 40, "medium": 400, "large": 10_000}


@pytest.fixture(scope="module", params=["tiny", "small", "medium"])
def portfolio(request) -> Portfolio:
    return generate(request.param)


@pytest.mark.parametrize("size", list(SIZES))
def test_each_size_has_its_pinned_content(size):
    assert generate(size).content_hash() == PINNED[size]


@pytest.mark.parametrize("size", list(SIZES))
def test_each_size_has_its_project_count(size):
    assert len(generate(size).projects) == COUNTS[size]


def test_the_same_seed_gives_the_same_portfolio_and_another_seed_does_not():
    assert generate("small", 5).to_json() == generate("small", 5).to_json()
    assert generate("small", 5).content_hash() != generate("small", 6).content_hash()


def test_an_unknown_size_is_refused_by_name():
    with pytest.raises(ValueError, match="huge"):
        generate("huge")


def test_project_ids_are_unique_and_every_asset_exists(portfolio):
    ids = portfolio.project_ids
    assert len(set(ids)) == len(ids)
    assets = {a.asset_id for a in portfolio.assets}
    assert all(p.asset_id in assets for p in portfolio.projects)


def test_every_project_fits_the_horizon_and_its_npv_covers_its_window(portfolio):
    last = portfolio.years[-1]
    for p in portfolio.projects:
        assert portfolio.years[0] <= p.earliest_start <= p.latest_start
        assert p.latest_start + p.duration - 1 <= last, p.project_id
        assert sorted(p.npv) == list(p.starts())
        assert p.program in PROGRAMS and p.region in REGIONS
        assert all(c > 0 for c in p.cost_profile)


def test_a_child_can_start_after_its_parent_and_never_belongs_to_an_alternative(portfolio):
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        if p.parent is not None:
            parent = by_id[p.parent]
            assert p.alt_group is None and parent.alt_group is None
            assert parent.earliest_start + p.parent_lag <= p.latest_start


def test_alternatives_come_in_pairs_on_one_asset(portfolio):
    groups: dict[str, list] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p)
    for members in groups.values():
        assert len(members) == 2
        assert len({m.asset_id for m in members}) == 1
        assert {m.intervention for m in members} == {"replace", "repair"}


def test_must_do_work_fits_every_budget_when_started_early(portfolio):
    spend = {y: 0 for y in portfolio.years}
    for p in portfolio.projects:
        if p.must_do:
            for year, amount in p.spend(p.earliest_start).items():
                spend[year] += amount
    assert all(spend[y] <= portfolio.budget[y] for y in portfolio.years)
    assert sum(p.capex for p in portfolio.projects if p.must_do) <= portfolio.capital_budget


def test_the_budget_forces_a_choice(portfolio):
    total = sum(p.capex for p in portfolio.projects)
    assert portfolio.capital_budget < total


def test_the_tiny_portfolio_has_one_of_each_relationship():
    tiny = generate("tiny")
    assert [p.project_id for p in tiny.projects if p.must_do] == ["P002"]
    assert [(p.project_id, p.parent) for p in tiny.projects if p.parent] == [("P004", "P003")]
    assert [p.project_id for p in tiny.projects if p.alt_group] == ["P006", "P007"]


def test_spend_shifts_the_cost_profile_to_the_start_year():
    p = generate("tiny").project("P003")
    assert p.spend(2027) == {2027: 980, 2028: 1490}
    with pytest.raises(ValueError):
        p.spend(2029)


@pytest.mark.parametrize("size", ["tiny", "small"])
def test_json_and_csv_round_trips_keep_the_content(size, tmp_path):
    original = generate(size)
    assert Portfolio.from_dict(original.to_dict()).content_hash() == original.content_hash()
    assert load_csv(save_csv(original, tmp_path)).content_hash() == original.content_hash()
