"""The outage layer on GridCap small: the jobs, and the first conflict the loop meets, checked by CP-SAT."""

from gridcap import generate

from outages import SEASONS, jobs, schedulable, minimal_conflict

small = generate("small")
outage = jobs(small)
print(f"{len(outage)} outage jobs; seasons (first week, week after the last): {SEASONS}")
for pid in ("P022", "P034", "P031"):
    j = outage[pid]
    print(f"{pid}: {j.weeks} weeks, between week {j.release} and week {j.deadline}")
chosen = [outage[pid] for pid in ("P022", "P031", "P034")]
print(f"P022+P031+P034 in one year: schedulable {schedulable(chosen)}")
print(f"minimal conflict: {[j.project_id for j in minimal_conflict(chosen)]}")
print(f"P031+P034 alone: schedulable {schedulable([outage['P031'], outage['P034']])}")
