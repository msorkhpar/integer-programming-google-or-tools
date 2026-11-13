from __future__ import annotations

import re


def mask_line(line: str) -> str:
    """The line with users, hosts, e-mail addresses and UUID-shaped keys replaced by placeholders."""
    # TODO: one re.sub per row of the statement's table.
    return line.upper()


if __name__ == "__main__":
    print(mask_line("No license found (user dock, host rack-9) for ops@example.com"))
