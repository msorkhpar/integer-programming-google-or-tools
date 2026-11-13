from __future__ import annotations

import hashlib
import json


def canonical(doc: dict) -> bytes:
    """The timetable's canonical bytes (its lists are already in a meaningful order)."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class Store:
    def __init__(self):
        self.files: dict[str, bytes] = {}           # digest -> bytes, as a bucket would hold them
        self.log: list[dict] = []                   # {"scenario", "version", "digest", "parent"}

    def put(self, doc: dict, scenario: str) -> str:
        data = canonical(doc)
        key = hashlib.sha256(data).hexdigest()
        if key not in self.files:
            self.files[key] = data
        mine = self.versions(scenario)
        if not mine or mine[-1]["digest"] != key:
            self.log.append({"scenario": scenario, "version": len(mine) + 1, "digest": key,
                             "parent": mine[-1]["digest"] if mine else None})
        return key

    def get(self, key: str) -> dict | None:
        data = self.files.get(key)
        if data is None or hashlib.sha256(data).hexdigest() != key:
            return None
        return json.loads(data)

    def versions(self, scenario: str) -> list[dict]:
        return [e for e in self.log if e["scenario"] == scenario]


if __name__ == "__main__":
    store = Store()
    key = store.put({"route": "12", "departures": ["06:10", "06:40"]}, "winter")
    print(key[:12], store.versions("winter"))
