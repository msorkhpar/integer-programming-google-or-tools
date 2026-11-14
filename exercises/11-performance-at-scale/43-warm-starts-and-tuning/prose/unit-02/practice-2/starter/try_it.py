"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from verdict import judge, sgm, verdict

# Work on five depot models with the old setting and a new one.
plan_old = [500.0, 800.0, 300.0, 1000.0, 650.0]
proof_old = [7000.0, 12000.0, 5000.0, 20000.0, 9000.0]
plan_fast = [v * 0.5 for v in plan_old]
proof_slow = [v * 1.4 for v in proof_old]

print("shifted mean of plan_old, shift 50:", round(sgm(plan_old, 50), 1))
print("plan_fast vs plan_old:", judge(plan_fast, plan_old, shift=50, margin=0.05))
print("faster plan, same proof:", verdict(plan_fast, plan_old, proof_old, proof_old, shift=50))
print("faster plan, slower proof:", verdict(plan_fast, plan_old, proof_slow, proof_old, shift=50))
print("same plan, slower proof:", verdict(plan_old, plan_old, proof_slow, proof_old, shift=50))
