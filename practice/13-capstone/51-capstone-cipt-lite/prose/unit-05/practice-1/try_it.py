"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from run_harness import NotDeterministic, canonical, differences, harness, manifest

tight = {"objective": "npv", "budget": {"2028": 150}}
m = manifest(tight)
result = m.get("result", {})
print("manifest sections:", sorted(m))
print("2028 budget 150, objective:", result.get("objective"), "status:", result.get("status"))
print("2028 budget 150, plan:", result.get("plan"))
print("differences from the count objective:", differences(m, manifest({"objective": "count", "budget": {"2028": 150}})))
print("harness, 3 fresh runs:", harness(tight, runs=3)[:16])
try:
    print("harness, count objective in set order:", harness({"objective": "count", "order": "set"}, runs=3)[:16])
except NotDeterministic as error:
    print("harness, count objective in set order:", error)
