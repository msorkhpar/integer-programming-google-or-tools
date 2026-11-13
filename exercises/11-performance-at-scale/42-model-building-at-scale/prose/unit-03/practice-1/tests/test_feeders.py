import os
import subprocess
import sys
from pathlib import Path

from feeders import generate_feeders

HERE = Path(__file__).resolve().parent


def test_the_same_seed_gives_the_same_feeders_with_their_ids():
    first, again = generate_feeders(30, seed=11), generate_feeders(30, seed=11)
    assert len(first) == 30 and first == again
    assert [f.feeder_id for f in first[:3]] == ["F00001", "F00002", "F00003"]


def test_every_value_is_in_its_range_and_they_vary():
    feeders = generate_feeders(400, seed=5)
    assert len(feeders) == 400
    assert all(1 <= f.length_km <= 40 and 50 <= f.customers <= 5_000 and 2 <= f.crew_days <= 20 for f in feeders)
    assert len({f.length_km for f in feeders}) > 30 and len({f.crew_days for f in feeders}) == 19


def test_a_larger_portfolio_starts_with_the_smaller_one():
    small, large = generate_feeders(10, seed=3), generate_feeders(1_000, seed=3)
    assert len(small) == 10 and large[:10] == small


def test_neighbouring_seeds_do_not_share_shifted_feeders():
    seven, eight = generate_feeders(20, seed=7), generate_feeders(20, seed=8)
    assert len(seven) == 20 and len(eight) == 20
    values = lambda fs: [(f.length_km, f.customers, f.crew_days) for f in fs]
    assert values(seven)[1:] != values(eight)[:19]
    assert values(seven) != values(eight)


def test_a_fresh_interpreter_with_other_string_hashing_gives_the_same_feeders():
    code = "from feeders import generate_feeders; print(generate_feeders(5, seed=9))"
    outputs = set()
    for hash_seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": hash_seed}
        done = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
        outputs.add(done.stdout)
    assert len(outputs) == 1 and "F00005" in outputs.pop()
