"""Roll the Ridge region's approved plan forward one year, carry it into the new model, check it, repair it."""

from cycles import next_cycle
from plan_model import broken, instance_set, keys, value
from runs import highs
from starts import carry_forward, greedy_fill, greedy_plan, repair, summary

ridge = instance_set()[0]
approved = highs(ridge, 1).plan                     # proved optimal (gap 0)
print(f"{ridge.name}, cycle {ridge.years[0]}-{ridge.years[-1]}: approved plan NPV {value(ridge, approved):,}, "
      f"{len(approved)} starts, {sum(t == ridge.years[0] for t in approved.values())} of them in {ridge.years[0]}")

nxt, committed = next_cycle(ridge, approved, seed=7)
old = {p.project_id: p for p in ridge.projects}
gone = sorted(i for i in old if i not in committed and all(p.project_id != i for p in nxt.projects))
revised = sorted(p.project_id for p in nxt.projects if p.project_id in old and p.cost_profile != old[p.project_id].cost_profile)
print(f"next cycle {nxt.years[0]}-{nxt.years[-1]}: {len(committed)} projects committed, {len(gone)} dropped, "
      f"{len(revised)} costs revised up 20%, {sum(p.project_id.startswith('N') for p in nxt.projects)} new projects")
print("budgets  " + " ".join(f"{y}" for y in nxt.years[:5]) + " ...")
print("  before " + " ".join(f"{ridge.budget[y] - sum(old[i].spend(ridge.years[0]).get(y, 0) for i in committed):>4}"
                             for y in nxt.years[:5]) + "    (last cycle's, less the committed spend)")
print("  now    " + " ".join(f"{nxt.budget[y]:>4}" for y in nxt.years[:5]))
print(f"model: {len(nxt.projects)} projects, {len(keys(nxt))} start variables")

carried, report = carry_forward(approved, nxt)
print("\ncarry forward:", ", ".join(f"{k} {len(v)}" for k, v in report.items()))
best = highs(nxt, 1).plan
print(f"{'carried':<12} {summary(nxt, carried)}")
fixed = repair(nxt, carried)
print(f"{'repaired':<12} {summary(nxt, fixed)}")
filled = greedy_fill(nxt, fixed)
print(f"{'filled':<12} {summary(nxt, filled)}")
print(f"{'greedy':<12} {summary(nxt, greedy_plan(nxt))}")
print(f"{'optimum':<12} {summary(nxt, best)}")

print("\nall eight regional plans, rolled forward the same way:")
print(f"{'cycle':<12} {'rows the carried plan breaks':>28} {'filled gap':>11} {'greedy gap':>11}")
for pf in instance_set():
    last = highs(pf, 1).plan
    n, _ = next_cycle(pf, last, seed=7)
    c, _ = carry_forward(last, n)
    opt = value(n, highs(n, 1).plan)
    f = value(n, greedy_fill(n, repair(n, c)))
    g = value(n, greedy_plan(n))
    print(f"{pf.name:<12} {len(broken(n, c)):>28} {(opt - f) / opt:>11.2%} {(opt - g) / opt:>11.2%}")
