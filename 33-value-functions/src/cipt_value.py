"""The CIPT value function on GridCap small: one coefficient per project and start year."""

from ortools.math_opt.python import mathopt

from benefits import measures
from gridcap import generate
from value_function import REFERENCE, WEIGHTS, normalized, npv_equivalent, raw, value_expression, value_table

small = generate("small")
v = value_table(small)
print(f"{len(v)} coefficients for {len(small.projects)} projects")

for pid in ("P030", "P006", "P019", "P035"):
    p = small.project(pid)
    for t in p.starts():
        score = normalized(raw(measures(small, p, t)), REFERENCE)
        parts = " ".join(f"{k[:3]} {WEIGHTS[k] * s:.4f}" for k, s in score.items())
        print(f"{pid} start {t}: {parts} | v {v[pid, t]:.4f} = ${npv_equivalent(v[pid, t]):,.0f}k NPV-equivalent")

m = measures(small, small.project("P006"), 2030)
print(f"P006 start 2030: NPV ${m.npv}k, {m.customer_minutes:,.0f} customer-minutes avoided")

model = mathopt.Model(name="cipt_value")
x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
     for p in small.projects for t in p.starts()}
plan_value = value_expression(x, v)
model.maximize(plan_value)              # section 8 adds the rules and solves; here we only read it

plan = {"P030": 2029, "P006": 2030, "P019": 2028}
values = {var: 1.0 if plan.get(pid) == t else 0.0 for (pid, t), var in x.items()}
print(f"plan {plan}: value {mathopt.evaluate_expression(plan_value, values):.4f}"
      f" (sum of its coefficients {sum(v[pid, t] for pid, t in plan.items()):.4f})")
