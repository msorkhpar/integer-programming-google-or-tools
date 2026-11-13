"""The replacement list as the asset team builds it today: worst condition first."""

from __future__ import annotations

from .fleet import Transformer


def worst_first(fleet: list[Transformer], budget: int) -> list[str]:
    """Walk down the condition ranking and take units until the next one does not fit the budget."""
    chosen, spent = [], 0
    for t in sorted(fleet, key=lambda t: (-t.condition, t.tid)):
        if spent + t.cost > budget:
            break
        chosen.append(t.tid)
        spent += t.cost
    return chosen
