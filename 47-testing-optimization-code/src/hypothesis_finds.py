"""Run the properties against each broken copy of the rules and print what Hypothesis reports.

For each bug, the properties run in order until one fails. Hypothesis then shrinks the failing case
to a small one and attaches it, with the test's notes, to the error; this program prints those
lines (and leaves out the "Explanation" Hypothesis adds after them, which names source lines).
"""

from __future__ import annotations

from bugs import BUGS, broken
from properties import PROPERTIES, plan_obeys_every_rule, property_test


def report(error: AssertionError) -> list[str]:
    notes = getattr(error, "__notes__", [])
    return notes[:notes.index("Explanation:")] if "Explanation:" in notes else notes


def main() -> None:
    for k, name in enumerate(BUGS, start=1):
        print(f"bug {k}: {name}")
        for check in PROPERTIES:
            try:
                property_test(check, broken(name), pinned=False)()
            except AssertionError as error:
                print(f"  caught by {check.__name__}")
                for line in report(error):
                    print("  " + line)
                break
        else:
            print("  no property failed")
    print("bug 3 again, with the shrunk case pinned as an @example:")
    try:
        property_test(plan_obeys_every_rule, broken("precedence ignores the lag"))()
    except AssertionError as error:
        for line in report(error):
            print("  " + line)


if __name__ == "__main__":
    main()
