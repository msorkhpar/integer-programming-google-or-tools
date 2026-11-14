"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from submit_check import problems

request = {
    "jobName": "solve-0107",
    "jobQueue": "depot-solves",
    "jobDefinition": "depot-solve",
    "containerOverrides": {
        "environment": [{"name": "SCENARIO", "value": "north"}],
        "resourceRequirements": [{"type": "VCPU", "value": "1"}, {"type": "MEMORY", "value": "4096"}],
    },
    "timeout": {"attemptDurationSeconds": 900},
    "retryStrategy": {"attempts": 3},
}
print("request solve-0107:", problems(request))

odd = {**request, "jobName": "-solve 7", "timeout": {"attemptDurationSeconds": 45}}
print("name '-solve 7', timeout 45 s:", problems(odd))

big = {**request, "retryStrategy": {"attempts": 12}, "containerOverrides": {
    "environment": [{"name": "SCENARIO", "value": "a"}, {"name": "SCENARIO", "value": "b"}],
    "resourceRequirements": [{"type": "VCPU", "value": "0.5"}, {"type": "MEMORY", "value": "8192"}]}}
print("12 attempts, 0.5 vCPU / 8192 MiB, SCENARIO twice:", problems(big))
