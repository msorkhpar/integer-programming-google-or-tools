"""Which settings make Hypothesis draw the same cases on every run?

Each run collects the cases one property test draws. Two runs are compared in one process, so
nothing but the settings differs between them. No model is solved here; the property only records.
"""

from __future__ import annotations

from hypothesis import given, seed, settings

from properties import CI
from strategies import cases


def drawn(config: settings, fixed_seed: int | None = None) -> list[str]:
    seen = []

    @config
    @given(cases())
    def record(case) -> None:
        seen.append(repr(case))

    if fixed_seed is not None:
        record = seed(fixed_seed)(record)
    record()
    return seen


def main() -> None:
    print("the built-in 'ci' profile:", settings.get_profile("ci"))
    print("this module's CI settings:", CI)
    random = settings(max_examples=60, database=None, deadline=None)
    for label, config, fixed in [("derandomize=True", CI, None), ("random, no seed", random, None),
                                 ("random, @seed(2027)", random, 2027)]:
        first, second = drawn(config, fixed), drawn(config, fixed)
        print(f"{label:<20} {len(first)} cases, then {len(second)}; same cases both times: {first == second}")
    print("first case under derandomize=True:", drawn(CI)[0])


if __name__ == "__main__":
    main()
