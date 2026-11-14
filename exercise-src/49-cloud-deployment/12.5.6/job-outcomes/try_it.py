"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from job_outcomes import outcomes

jobs = {
    "lint": {},
    "unit": {},
    "build": {"needs": ["lint", "unit"]},
    "release": {"needs": "build", "if": "github.event_name == 'push'"},
    "report": {"needs": "release", "if": "always()"},
}

print("push, nothing failing:", outcomes(jobs, "push"))
print("pull_request:", outcomes(jobs, "pull_request"))
print("push, unit failing:", outcomes(jobs, "push", failing={"unit"}))
