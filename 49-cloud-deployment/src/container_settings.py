"""Lesson 12.5.1: the worker reads its settings from the environment and refuses to start on any problem.

The three environments are what three `docker run -e ...` commands (or three Batch submissions)
would pass. The digest is a placeholder of the right shape. GridCap is a fictional utility.
"""

from settings import BadSettings, Settings

DIGEST = "730c8b40b1eb" + "0" * 52
environments = {
    "as Batch starts it": {"RESULT_BUCKET": "gridcap-runs-example", "RUN_ID": "run-0007",
                           "SNAPSHOT_DIGEST": DIGEST, "TIME_LIMIT_S": "120"},
    "no time limit set": {"RESULT_BUCKET": "gridcap-runs-example", "RUN_ID": "run-0008",
                          "SNAPSHOT_DIGEST": DIGEST},
    "three mistakes": {"RUN_ID": "run-0009", "SNAPSHOT_DIGEST": "730c8b40b1eb", "TIME_LIMIT_S": "ten"},
}
for label, env in environments.items():
    try:
        s = Settings.from_env(env)
        print(f"{label:<19} run {s.run_id}, bucket {s.bucket}, limit {s.time_limit_s:g} s")
    except BadSettings as error:
        print(f"{label:<19} refused: {error}")
