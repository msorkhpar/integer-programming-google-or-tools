"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from timetables import Store

spring = {"route": "7", "depot": "Quay", "departures": ["05:50", "06:20", "06:50"]}
thin = {"route": "7", "depot": "Quay", "departures": ["05:50", "06:50"]}

store = Store()
a = store.put(spring, "spring")
b = store.put(thin, "spring")
print("put spring twice gives the same key:", store.put(spring, "spring") == a)
print("files held:", len(store.files))
for entry in store.versions("spring"):
    print("version", entry["version"], "digest", entry["digest"][:10], "parent", (entry["parent"] or "-")[:10])
print("get the thin key:", store.get(b))
if b in store.files:
    store.files[b] = store.files[b].replace(b"05:50", b"05:55")
print("get the thin key after its bytes changed:", store.get(b))
