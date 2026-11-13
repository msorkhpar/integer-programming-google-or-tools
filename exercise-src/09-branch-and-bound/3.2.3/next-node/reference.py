from __future__ import annotations


def next_node(waiting: list[tuple[int, int, float]], rule: str) -> int:
    """The id of the waiting node `rule` takes next. Nodes are (id, depth, bound)."""
    if rule == "depth":
        return max(waiting, key=lambda n: (n[1], n[0]))[0]
    if rule == "best":
        return max(waiting, key=lambda n: (n[2], -n[0]))[0]
    if rule == "breadth":
        return min(waiting, key=lambda n: n[0])[0]
    raise ValueError(f"unknown rule {rule!r}")


if __name__ == "__main__":
    waiting = [(3, 2, 410.0), (6, 3, 395.5), (5, 3, 402.0)]
    for rule in ("depth", "best", "breadth"):
        print(rule, next_node(waiting, rule))
