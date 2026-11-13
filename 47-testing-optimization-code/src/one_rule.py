"""Run every one-rule unit test against the correct rules and against each broken copy.

A cell reads "pass" when the test passed and "FAIL" when an assertion failed, that is, when the
test caught the bug. Then, for each bug, the assertion that caught it.
"""

from __future__ import annotations

import traceback

from bugs import BUGS, broken
from plan_model import RULES
from rule_tests import TESTS


def outcome(test, rules: dict) -> str | None:
    """None if the test passed, else the source line of the assertion that failed."""
    try:
        test(rules)
    except AssertionError as error:
        return traceback.extract_tb(error.__traceback__)[-1].line
    return None


def main() -> None:
    labels = ["correct"] + [f"bug {k}" for k in range(1, len(BUGS) + 1)]
    for k, name in enumerate(BUGS, start=1):
        print(f"bug {k}: {name}")
    print(f"{'':<40}" + "".join(f"{label:<9}" for label in labels))
    columns = [RULES] + [broken(name) for name in BUGS]
    for test in TESTS:
        cells = "".join(f"{'pass' if outcome(test, rules) is None else 'FAIL':<9}" for rules in columns)
        print(f"{test.__name__:<40}{cells}")
    print("the assertion that caught each bug:")
    for k, name in enumerate(BUGS, start=1):
        for test in TESTS:
            line = outcome(test, broken(name))
            if line:
                print(f"  bug {k}  {test.__name__}: {line}")


if __name__ == "__main__":
    main()
