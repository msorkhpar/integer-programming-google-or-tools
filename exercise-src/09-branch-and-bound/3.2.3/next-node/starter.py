from __future__ import annotations


def next_node(waiting: list[tuple[int, int, float]], rule: str) -> int:
    """The id of the waiting node `rule` takes next. Nodes are (id, depth, bound)."""
    # TODO: depth: greatest depth, newest first; best: highest bound, oldest first;
    # breadth: oldest.
    return -1


if __name__ == "__main__":
    waiting = [(3, 2, 410.0), (6, 3, 395.5), (5, 3, 402.0)]
    for rule in ("depth", "best", "breadth"):
        print(rule, next_node(waiting, rule))
