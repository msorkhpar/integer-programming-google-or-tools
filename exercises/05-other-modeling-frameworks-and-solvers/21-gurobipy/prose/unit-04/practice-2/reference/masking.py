from __future__ import annotations

import re

RULES = [
    (re.compile(r"\buser [^,)]*"), "user <user>"),
    (re.compile(r"\bhost [^,)]*"), "host <host>"),
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "<email>"),
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "<key>"),
]


def mask_line(line: str) -> str:
    """The line with users, hosts, e-mail addresses and UUID-shaped keys replaced by placeholders."""
    for pattern, placeholder in RULES:
        line = pattern.sub(placeholder, line)
    return line


if __name__ == "__main__":
    print(mask_line("No license found (user dock, host rack-9) for ops@example.com"))
