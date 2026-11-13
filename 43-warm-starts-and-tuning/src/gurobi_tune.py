"""Gurobi's own tuning tool on one regional plan: how to call it, and what of its answer can be quoted."""

import os
import shutil
import tempfile

from grb_runs import build_gurobi, quiet_env
from plan_model import instance_set

ridge = instance_set()[0]
env = quiet_env()
model, _ = build_gurobi(env, ridge)
model.Params.Threads = 1
model.Params.TuneTimeLimit = 10        # seconds on the clock for the whole search
model.Params.TuneTrials = 2            # each candidate setting is solved with two seeds
model.Params.TuneOutput = 0            # no tuning log
limit, trials = model.Params.TuneTimeLimit, model.Params.TuneTrials
model.tune()

found = []
with tempfile.TemporaryDirectory() as folder:
    for k in range(model.TuneResultCount):
        model.getTuneResult(k)             # copies parameter set k into the model
        path = os.path.join(folder, f"set{k}.prm")
        model.write(path)                  # a .prm file lists the parameters that differ from the defaults
        with open(path) as f:
            found.append([line.split()[0] for line in f if line.strip() and not line.startswith("#")])

print(f"tuned {ridge.name} for {limit:g} s of wall-clock time, {trials} trials per setting, one thread")
print("parameter sets kept: <masked>; parameters they change: <masked>")
print("every set kept changes Threads, which the program set itself:", all("Threads" in s for s in found))
print("the grbtune command line, which tunes several models at once, is on this machine:",
      shutil.which("grbtune") is not None)
