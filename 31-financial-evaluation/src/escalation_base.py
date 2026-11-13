"""Escalation counted from the price base year, or from the project's own start: P022, three starts.

The second convention is a common shortcut: the k-th year of work is escalated by (1 + e) ** k
whatever year the work starts. Both columns discount to 2027
at 7% the same way, so the only difference is where escalation starts counting.
"""

from gridcap import generate

from finance import escalate, present_value

p = generate("small").project("P022")
price_year, e, rate = 2027, 0.03, 0.07
print("start  nominal from 2027  nominal from start   PV from 2027  PV from start")
for start in p.starts():
    from_base = {start + k: escalate(c, e, start + k - price_year) for k, c in enumerate(p.cost_profile)}
    from_start = {start + k: escalate(c, e, k) for k, c in enumerate(p.cost_profile)}
    print(f"{start}  {sum(from_base.values()):>17,.1f}  {sum(from_start.values()):>18,.1f}"
          f"  {present_value(from_base, rate, 2027):>13,.1f}  {present_value(from_start, rate, 2027):>13,.1f}")
