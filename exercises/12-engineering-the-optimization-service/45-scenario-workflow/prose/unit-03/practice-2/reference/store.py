from __future__ import annotations

import copy


class Store:
    """Plans kept with a version number; a save must name the version it read."""

    def __init__(self):
        self._plans: dict[str, tuple[dict, int]] = {}

    def create(self, plan_id: str, plan: dict) -> int:
        self._plans[plan_id] = (copy.deepcopy(plan), 1)
        return 1

    def read(self, plan_id: str) -> tuple[dict, int]:
        """A private copy of the plan, and its version."""
        plan, version = self._plans[plan_id]
        return copy.deepcopy(plan), version

    def save(self, plan_id: str, read_version: int, plan: dict) -> int | None:
        """Store the plan and return its new version, or None if someone saved since read_version."""
        _, version = self._plans[plan_id]
        if version != read_version:
            return None
        self._plans[plan_id] = (copy.deepcopy(plan), version + 1)
        return version + 1


if __name__ == "__main__":
    store = Store()
    store.create("D-1", {"roofs": 400})
    plan, v = store.read("D-1")
    plan["roofs"] = 350
    print(store.save("D-1", v, plan), store.save("D-1", v, plan))
