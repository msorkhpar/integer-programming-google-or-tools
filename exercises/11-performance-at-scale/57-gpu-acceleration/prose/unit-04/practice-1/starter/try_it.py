"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from repeats import bits_promised, verdict


def run(**changes):
    base = {"inputs": "depot-lp-v3", "device": "cpu", "solver": "highs", "method": "ipm", "threads": 1,
            "tolerance": 1e-8, "versions": "highspy 1.14.0", "kind": "lp", "objective": 7_340.25, "digest": "c0"}
    return {**base, **changes}


print("same run twice:", verdict(run(), run(), 1e-6))
print("same config, digest c1:", verdict(run(), run(digest="c1"), 1e-6))
print("gpu pdlp, objective 7340.2500001:", verdict(run(), run(device="gpu", method="pdlp", objective=7_340.2500001), 1e-6))
print("gpu pdlp, objective 7341:", verdict(run(), run(device="gpu", method="pdlp", objective=7_341.0), 1e-6))
print("inputs depot-lp-v4:", verdict(run(), run(inputs="depot-lp-v4"), 1e-6))
print("bits promised, cuopt milp twice:", bits_promised(run(solver="cuopt", kind="milp", method="milp"),
                                                         run(solver="cuopt", kind="milp", method="milp")))
