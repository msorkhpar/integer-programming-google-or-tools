"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from error_routing import route

load = {
    "Type": "Task",
    "Retry": [{"ErrorEquals": ["Feed.Slow"], "MaxAttempts": 1},
              {"ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 2}],
    "Catch": [{"ErrorEquals": ["Feed.Corrupt"], "Next": "Quarantine"},
              {"ErrorEquals": ["States.ALL"], "Next": "PageOnCall"}],
}

print("Feed.Slow:", route(load, ["Feed.Slow"]))
print("Feed.Slow twice:", route(load, ["Feed.Slow", "Feed.Slow"]))
print("Feed.Corrupt three times:", route(load, ["Feed.Corrupt"] * 3))
print("States.Timeout:", route(load, ["States.Timeout"]))
print("no errors:", route(load, []))
