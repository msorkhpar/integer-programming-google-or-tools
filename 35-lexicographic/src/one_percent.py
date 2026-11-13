"""Section 8's milestone: the plan that keeps NPV within 1% of its best and then removes the most risk."""

from gridcap import generate
from lex_model import build, score
from lexicographic import Level, allowed_loss, solve_levels

small = generate("small")
sm = build(small)

npv_plan = solve_levels(sm, [Level("npv")]).plan
levels = [Level("npv", rel_tol=0.01), Level("risk")]
out = solve_levels(sm, levels)
plan = out.plan
print(f"pass 1: best NPV ${out.best['npv']:,.0f}k, allowed loss ${allowed_loss(out.best['npv'], levels[0]):,.1f}k,"
      f" floor ${out.floor['npv']:,.1f}k")
print(f"pass 2: most risk removed with NPV >= floor: ${out.best['risk']:,.1f}k")
for label, p in (("NPV plan", npv_plan), ("1% plan", plan)):
    print(f"{label:9} NPV ${score(sm, p, 'npv'):,.0f}k  risk removed ${score(sm, p, 'risk'):,.1f}k  projects {len(p)}")

print("project  NPV plan  1% plan     NPV    risk  name")
for pid in sorted(set(npv_plan) | set(plan)):
    before, after = npv_plan.get(pid), plan.get(pid)
    if before == after:
        continue
    d_npv = sm.coef["npv"].get((pid, after), 0) - sm.coef["npv"].get((pid, before), 0)
    d_risk = sm.coef["risk"].get((pid, after), 0) - sm.coef["risk"].get((pid, before), 0)
    print(f"{pid:7} {str(before or '-'):>9} {str(after or '-'):>8} {d_npv:+7,.0f} {d_risk:+7,.1f}  "
          f"{small.project(pid).name}")

third = solve_levels(sm, levels + [Level("npv")]).plan        # pass 3: NPV again, risk kept at its best
print(f"pass 3 (NPV again, risk kept): NPV ${score(sm, third, 'npv'):,.0f}k  "
      f"risk removed ${score(sm, third, 'risk'):,.1f}k")
