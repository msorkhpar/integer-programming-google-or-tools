"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from policy import decide

workstation = {"gpu": True, "cuopt": True, "cores": 24}
gpu_no_cuopt = {"gpu": True, "cuopt": False, "cores": 12}
small_vm = {"gpu": False, "cuopt": False, "cores": 2}

print("lp 1.2M nonzeros, explore, workstation:", decide({"kind": "lp", "nonzeros": 1_200_000, "use": "explore"}, workstation))
print("lp 1.2M nonzeros, bound, small vm:", decide({"kind": "lp", "nonzeros": 1_200_000, "use": "bound"}, small_vm))
print("lp 80k nonzeros, explore, workstation:", decide({"kind": "lp", "nonzeros": 80_000, "use": "explore"}, workstation))
print("milp, explore, workstation:", decide({"kind": "milp", "nonzeros": 60_000, "use": "explore"}, workstation))
print("milp, explore, gpu without cuopt:", decide({"kind": "milp", "nonzeros": 60_000, "use": "explore"}, gpu_no_cuopt))
print("milp, publish, workstation:", decide({"kind": "milp", "nonzeros": 60_000, "use": "publish"}, workstation))
