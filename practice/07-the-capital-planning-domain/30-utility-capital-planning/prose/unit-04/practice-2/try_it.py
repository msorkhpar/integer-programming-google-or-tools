"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from worksheet import by_stakeholder, trace

reqs = [{"id": "R1", "stakeholder": "board", "text": "stay within the five-year cap"},
        {"id": "R2", "stakeholder": "board", "text": "replace every failed main"},
        {"id": "R3", "stakeholder": "regulator", "text": "publish the risk score"},
        {"id": "R4", "stakeholder": "regulator", "text": "keep crews within hours"}]
checks = [{"name": "cap", "covers": ["R1"], "passed": True},
          {"name": "mains", "covers": ["R2", "R4"], "passed": True},
          {"name": "hours", "covers": ["R4"], "passed": False}]

status = trace(reqs, checks)
print("status per requirement:", status)
print("counts per stakeholder:", by_stakeholder(reqs, status))
