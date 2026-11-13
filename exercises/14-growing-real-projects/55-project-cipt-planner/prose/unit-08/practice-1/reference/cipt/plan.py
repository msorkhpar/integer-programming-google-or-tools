"""A plan: what the solve decided, in the planners' terms."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Plan:
    """The answer to a request.

    `status` is "optimal", "infeasible" or another solver outcome in lower case; `starts` maps each
    funded project to the year its work starts; `objective` is what the model maximized; `npv` and
    `risk` are the plan's NPV and the risk it removes, both in $k, whichever was maximized.
    """

    status: str
    starts: dict[str, int] = field(default_factory=dict)
    objective: float = 0.0
    npv: float = 0.0
    risk: float = 0.0

    @property
    def funded(self) -> tuple[str, ...]:
        return tuple(sorted(self.starts))
