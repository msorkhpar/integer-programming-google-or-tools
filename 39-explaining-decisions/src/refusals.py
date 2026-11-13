"""On a MILP, a row with slack can still be the row that blocks (lesson 9.3.1).

For every project GridCap small's best plan leaves out, and every year it could start, add it to
the plan as it stands and list the rows that break.
"""

from collections import Counter

from gridcap import generate

from binding import refusals, slack_table
from explain_model import build, solve

small = generate("small")
built = build(small)
run = solve(built)
refused = refusals(built, run.plan)
room = {name: s for name, _, s in slack_table(built, run.plan)}

fits = [key for key, broken in refused.items() if not broken]
print(f"{len(refused)} single additions tried, {len(fits)} fit")
print()

count = Counter(name for broken in refused.values() for name in broken)
print("row          slack  refuses")
for name in sorted(count, key=lambda n: (n.split("_")[0] != "budget", n)):
    print(f"{name:11}  {room[name]:5,.0f}  {count[name]:2} of {len(refused)}")
print()

for pid in ("P004", "P037", "P002"):
    project = small.project(pid)
    for t in project.starts():
        needs = ", ".join(f"{name} (needs {project.spend(t)[int(name[-4:])]:,}, slack {room[name]:,.0f})"
                          if name.startswith("budget") else f"{name} (slack {room[name]:,.0f})"
                          for name in refused[pid, t])
        print(f"add {pid} in {t}: breaks {needs}")
