from __future__ import annotations

import re

CODE_NAMES = {3: "INVALID_ARGUMENT", 9: "FAILED_PRECONDITION", 12: "UNIMPLEMENTED", 13: "INTERNAL"}
SUFFIX = re.compile(r"^(?P<message>.*) \(was C\+\+ (?P<code>[A-Z_]+)\)$", re.S)


def refusal(error: BaseException) -> tuple[str, str]:
    """(status code name, message) of a refused solve, whichever way OR-Tools raised it."""
    hidden = error.__context__
    if hidden is not None and hasattr(hidden, "code") and hasattr(hidden, "message"):
        return CODE_NAMES.get(hidden.code, "UNKNOWN"), hidden.message
    match = SUFFIX.match(str(error))
    if match:
        return match["code"], match["message"]
    return "UNKNOWN", str(error)


if __name__ == "__main__":
    print(refusal(ValueError("threads not supported (was C++ INVALID_ARGUMENT)")))
