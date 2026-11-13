from __future__ import annotations


def in_force(entries: list[dict]) -> dict[str, tuple]:
    """{project: (kind, year)} in force after replaying the audit entries in the order they were made."""
    active: dict[str, tuple] = {}
    # TODO: replay the entries.
    return active


if __name__ == "__main__":
    trail = [{"seq": 1, "action": "set", "project": "M-12", "kind": "start_in", "year": 2028, "by": "engineer-a"}]
    print(in_force(trail))
