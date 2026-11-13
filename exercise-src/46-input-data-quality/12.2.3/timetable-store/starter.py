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
        # TODO: store the content under its digest, log a new version when it is one, return the digest.
        return ""

    def get(self, key: str) -> dict | None:
        # TODO: the stored timetable, or None when it is missing or its bytes no longer match the key.
        return None

    def versions(self, scenario: str) -> list[dict]:
        return [e for e in self.log if e["scenario"] == scenario]


if __name__ == "__main__":
    store = Store()
    key = store.put({"route": "12", "departures": ["06:10", "06:40"]}, "winter")
    print(key[:12], store.versions("winter"))
