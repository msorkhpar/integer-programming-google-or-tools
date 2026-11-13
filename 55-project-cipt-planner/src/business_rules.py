"""Lesson 14.2.3: the step-02 plan read against the planners' rules, then the plan that keeps them.

GridCap small is a fictional utility's portfolio; its bundle (P011 with P012) is declared in
export.py. `broken` checks a plan against the rules using the export alone, never the model, so a
wrong row cannot approve its own plan. Last, it plans the demo export with every order of RULES,
and with each project's start variables made latest year first, to see which of several tied plans
HiGHS returns.
"""

import itertools
import json
from collections import Counter

from export import gridcap_export
from steps import STEPS, use

raw = gridcap_export("small")
rows = {r["id"]: r for r in raw["projects"]}


def broken(starts: dict[str, int]) -> list[str]:
    found = [f"must-do {pid} not funded" for pid, r in rows.items() if r["must_do"] and pid not in starts]
    for column, word in (("alt_group", "alternatives"), ("bundle", "bundle")):
        groups: dict[str, list[str]] = {}
        for pid, r in rows.items():
            if r[column]:
                groups.setdefault(r[column], []).append(pid)
        for g, members in sorted(groups.items()):
            funded = [m for m in members if m in starts]
            if column == "alt_group" and len(funded) > 1:
                found.append(f"{word} {g}: {' and '.join(funded)} both funded")
            if column == "bundle" and 0 < len(funded) < len(members):
                found.append(f"{word} {g}: only {', '.join(funded)} of {', '.join(members)} funded")
    for pid, r in rows.items():
        if pid in starts and r["parent"]:
            parent_start = starts.get(r["parent"])
            if parent_start is None or parent_start > starts[pid] - r["parent_lag"]:
                found.append(f"{pid} starts {starts[pid]}, its parent {r['parent']} "
                             f"{'is not funded' if parent_start is None else f'starts {parent_start}'}")
    return found


old = use(2)
plan = old.solve.solve(old.data.load_request(raw))
problems = broken(plan.starts)
print(f"step 02 plan: value ${plan.objective:,.0f}k, {len(problems)} rules broken")
for line in problems:
    print(f"  {line}")

new = use(3)
request = new.data.load_request(raw)
built = new.model.build(request)
kinds = Counter(name.split("_")[0] for name in built.rows)
print("step 03 rows: " + ", ".join(f"{kind} {n}" for kind, n in sorted(kinds.items())))
plan = new.solve.solve(request)
print(f"step 03 plan: value ${plan.objective:,.0f}k, {len(broken(plan.starts))} rules broken, "
      f"{len(plan.starts)} projects funded")

# Ties: which of several equally good plans HiGHS returns can depend on how the model was built.
demo = new.data.load_request(json.loads((STEPS / "03" / "data" / "demo.json").read_text(encoding="utf-8")))
rules = new.rules.RULES
plans = set()
for order in itertools.permutations(rules):
    new.model.RULES = order
    plans.add(tuple(sorted(new.solve.solve(demo).starts.items())))
new.model.RULES = rules
print(f"demo, every one of the {len(list(itertools.permutations(rules)))} orders of RULES: {len(plans)} plan")
first = new.solve.solve(demo)
window = new.data.Request.starts
new.data.Request.starts = lambda self, project: window(self, project)[::-1]
late = new.solve.solve(demo)
new.data.Request.starts = window
moved = ", ".join(f"{pid} {first.starts[pid]} -> {late.starts[pid]}" for pid in first.funded
                  if late.starts.get(pid) != first.starts[pid])
print(f"demo, start variables made latest year first: value ${first.objective:,.0f}k -> "
      f"${late.objective:,.0f}k, {moved}")
