from __future__ import annotations

import re

CODE_NAMES = {3: "INVALID_ARGUMENT", 9: "FAILED_PRECONDITION", 12: "UNIMPLEMENTED", 13: "INTERNAL"}


def refusal(error: BaseException) -> tuple[str, str]:
    """(status code name, message) of a refused solve, whichever way OR-Tools raised it."""
    # TODO: the hidden status first, then the '(was C++ ...)' suffix, then UNKNOWN.
    return "", ""


if __name__ == "__main__":
    print(refusal(ValueError("threads not supported (was C++ INVALID_ARGUMENT)")))
