"""Risk removed year by year by one project, for each year it may start in."""

from asset_curves import AGE_AFTER, ages_by_year, yearly_reduction
from gridcap import generate

small = generate("small")
p = small.project("P024")
a = small.asset(p.asset_id)
keep, window = AGE_AFTER[p.intervention], tuple(range(2027, 2037))
print(f"{p.project_id} {p.intervention} {a.asset_id} ({a.kind}): age {a.age} in 2027, beta {a.weibull_beta}, "
      f"eta {a.weibull_eta}, CoF ${a.cof:,}k, {p.duration} years of work, keeps {keep:.0%} of its age")
print("start | asset age by year, 2027-2036")
for s in p.starts():
    ages = ages_by_year(a.age, window, s, p.duration, keep)
    print(f" {s} | " + " ".join(f"{ages[y]:>4.0f}" for y in window))
print("start | risk removed by year, $k, 2027-2036               | plan years | ten years")
for s in p.starts():
    cut = yearly_reduction(a, window, s, p.duration, keep)
    print(f" {s} | " + " ".join(f"{cut[y]:>4.0f}" for y in window)
          + f" | {sum(cut[y] for y in small.years):>10.0f} | {sum(cut.values()):>9.0f}")
