"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pick import pick

# Benchmark evidence per solver: runs solved, runs made, repeatable, spread of its work.
evidence = {
    "Alder": {"solved": 10, "runs": 10, "repeat": True, "spread": 1.6},
    "Beech": {"solved": 10, "runs": 10, "repeat": True, "spread": 1.3},
    "Cherry": {"solved": 9, "runs": 10, "repeat": True, "spread": 1.1},
    "Dogwood": {"solved": 10, "runs": 10, "repeat": False, "spread": 1.0},
}
print("passing Alder, Beech, Cherry, Dogwood:", pick(["Alder", "Beech", "Cherry", "Dogwood"], evidence))
print("passing Alder, Cherry:", pick(["Alder", "Cherry"], evidence))
print("passing Cherry, Elder (unmeasured):", pick(["Cherry", "Elder"], evidence))
