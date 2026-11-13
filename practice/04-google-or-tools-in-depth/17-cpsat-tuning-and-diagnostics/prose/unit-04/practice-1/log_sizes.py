from __future__ import annotations

import re

VARIABLES = re.compile(r"#Variables: ([\d']+)")


def variables_in(log: str, header: str) -> int:
    """The #Variables count of the model block that starts with `header`."""
    # TODO: find the header line, then the first #Variables line after it.
    return 0


def variables_before_and_after(log: str) -> tuple[int, int]:
    """Variables in the model as written and after presolve."""
    return (variables_in(log, "Initial optimization model"),
            variables_in(log, "Presolved optimization model"))


if __name__ == "__main__":
    sample = ("Initial optimization model '': (model_fingerprint: 0x1)\n#Variables: 12 (#bools: 12 in objective)\n"
              "Presolved optimization model '': (model_fingerprint: 0x2)\n#Variables: 9 (#bools: 9 in objective)\n")
    print(variables_before_and_after(sample))
