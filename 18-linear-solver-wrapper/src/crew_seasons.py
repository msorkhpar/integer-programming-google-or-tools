"""Lesson 4.7.4: pack GridCap small's distribution and vegetation work into 12-month crew seasons.

Each project is a bundle of crew-months that one crew does whole; a contract crew is hired for a
season of 12 crew-months. How few crews cover the work? GridCap is a fictional utility's portfolio,
and the season length is invented for this lesson.
"""

from bin_packing import first_fit_decreasing, lower_bound, pack
from gridcap import generate

SEASON = 12                                            # crew-months one hired crew works

small = generate("small")
work = [p for p in small.projects if p.program in ("distribution", "vegetation")]
sizes = [p.crew_months for p in work]
print(f"{len(work)} projects, {sum(sizes)} crew-months, largest {max(sizes)}; "
      f"seasons of {SEASON}: at least {lower_bound(sizes, SEASON)} crews")

ffd = first_fit_decreasing(sizes, SEASON)
print(f"first fit decreasing: {len(ffd)} crews, loads {sorted((sum(sizes[i] for i in b) for b in ffd), reverse=True)}")

print(f"first fit decreasing meets the bound, so it is optimal: {len(ffd) == lower_bound(sizes, SEASON)}")
result, packing = pack(sizes, SEASON, max_bins=len(ffd))     # FFD's count is enough bins to offer
print(f"MIP, as a check: {result.termination.reason.name}, {len(packing)} crews")
for b, items in enumerate(packing):
    print(f"  crew {b + 1}: {' '.join(work[i].project_id for i in items):32} {sum(sizes[i] for i in items):2} crew-months")
