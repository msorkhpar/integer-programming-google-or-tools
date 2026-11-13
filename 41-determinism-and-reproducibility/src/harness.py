"""Lesson 10.2.5: the deterministic run harness.

`check(config, runs)` solves the same config `runs` times, each in a fresh process with its own hash
seed (repeat.py), and compares the manifests byte for byte. If any run differs from the first it
raises `NotDeterministic`, naming the run and every field that changed; otherwise it returns the
manifest and its digest. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

from manifest import canonical, sha256
from repeat import repeat


class NotDeterministic(AssertionError):
    """Two runs of one config gave different manifests."""


def diff(a, b, path: str = "") -> list[str]:
    """The paths at which two manifests differ; a list is compared whole and reported once."""
    if isinstance(a, dict) and isinstance(b, dict):
        found = []
        for key in sorted(set(a) | set(b)):
            where = f"{path}.{key}" if path else key
            if key not in a or key not in b:
                found.append(where)
            else:
                found += diff(a[key], b[key], where)
        return found
    return [] if a == b else [path]


def check(config: dict, runs: int = 10) -> tuple[dict, str]:
    """Raise NotDeterministic unless every run's manifest has the same bytes as the first."""
    manifests = [record["manifest"] for record in repeat(config, runs)]
    first = canonical(manifests[0])
    for k, manifest in enumerate(manifests[1:], start=2):
        if canonical(manifest) != first:
            raise NotDeterministic(f"run {k} of {runs} differs from run 1 at: "
                                   + ", ".join(diff(manifests[0], manifest)))
    return manifests[0], sha256(manifests[0])


if __name__ == "__main__":
    good = [
        ("HiGHS, highest NPV, GridCap small",
         {"size": "small", "objective": "npv", "solver": "highs", "params": {"relative_gap_tolerance": 0.0}}),
        ("CP-SAT, 1 worker, seed 7, GridCap small",
         {"size": "small", "objective": "npv", "solver": "cpsat", "params": {"num_workers": 1, "random_seed": 7}}),
        ("CP-SAT, 4 workers interleaved, seed 7, deterministic limit 2, GridCap medium",
         {"size": "medium", "objective": "npv", "solver": "cpsat",
          "params": {"num_workers": 4, "interleave_search": True, "random_seed": 7, "max_deterministic_time": 2.0}}),
    ]
    for label, config in good:
        manifest, digest = check(config, runs=10)
        result = manifest["result"]
        print(f"PASS {label}: 10 identical manifests, sha256 {digest[:16]}, "
              f"{result['status']} {result['objective']:,.0f}")
    bad = [
        ("HiGHS, most projects, projects in set order, GridCap small",
         {"size": "small", "objective": "count", "order": "set", "solver": "highs",
          "params": {"relative_gap_tolerance": 0.0}}),
        ("CP-SAT, 4 workers, seed 7, deterministic limit 2, GridCap medium",
         {"size": "medium", "objective": "npv", "solver": "cpsat",
          "params": {"num_workers": 4, "random_seed": 7, "max_deterministic_time": 2.0}}),
    ]
    for label, config in bad:
        try:
            check(config, runs=5)
            print(f"PASS {label}")
        except NotDeterministic as error:
            print(f"FAIL {label}:\n     {error}")
