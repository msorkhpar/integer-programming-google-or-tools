"""GridCap large from its seed: the same bytes in this process, in fresh interpreters, at every run.

`content_hash()` is the sha256 of the portfolio's canonical JSON, so equal hashes mean equal
portfolios, field for field. gridcap's own tests pin the hash of each size at the default seed.
GridCap is fictional.
"""

from __future__ import annotations

import os
import subprocess
import sys

from gridcap import DEFAULT_SEED, generate
from stopwatch import measure

PINNED_LARGE = "092cac4f6f56f699439d198d829a459f557c8f05e8844029dcce1878dd99d593"   # pinned by gridcap's own tests
CHILD = "from gridcap import generate; print(generate('large').content_hash())"


def in_fresh_interpreter(hash_seed: str) -> str:
    """Generate large in a new Python process whose string hashing is salted differently."""
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    return subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True,
                          check=True).stdout.strip()


if __name__ == "__main__":
    large = generate("large")
    digest = large.content_hash()
    print(f"seed {DEFAULT_SEED}: {len(large.projects):,} projects, hash {digest[:16]}..., pinned: {digest == PINNED_LARGE}")
    print("same seed, generated again here:     ", generate("large").content_hash() == digest)
    for hash_seed in ("1", "2"):
        print(f"fresh interpreter, PYTHONHASHSEED={hash_seed}:", in_fresh_interpreter(hash_seed) == digest)
    for seed in (2028, 2029):
        other = generate("large", seed)
        same_ids = sum(a.project_id == b.project_id and a.cost_profile == b.cost_profile
                       for a, b in zip(large.projects, other.projects))
        print(f"seed {seed}: hash {other.content_hash()[:16]}..., projects with the same id and cost profile: {same_ids:,}")
    print()
    print("measured:", "generate('large')", measure(lambda: generate("large"), repeats=5))
