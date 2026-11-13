"""After the work the asset ages again: a frozen post-work risk overstates the reduction."""

from asset_curves import AGE_AFTER, ages_by_year, yearly_reduction, yearly_risk
from gridcap import generate

small = generate("small")
window = tuple(range(2027, 2037))


def frozen_reduction(a, start: int, duration: int, keep: float) -> dict[int, float]:
    """The shortcut: after the work, risk stays at its value on the day the work ends."""
    done = start + duration
    after = yearly_risk(keep * (a.age + done - window[0]), a.weibull_beta, a.weibull_eta, a.cof)
    return {y: yearly_risk(a.age + y - window[0], a.weibull_beta, a.weibull_eta, a.cof) - after if y >= done else 0.0
            for y in window}


for pid, start in (("P024", 2028), ("P027", 2029)):
    p = small.project(pid)
    a = small.asset(p.asset_id)
    keep = AGE_AFTER[p.intervention]
    aging = yearly_reduction(a, window, start, p.duration, keep)
    frozen = frozen_reduction(a, start, p.duration, keep)
    ages = ages_by_year(a.age, window, start, p.duration, keep)
    print(f"{pid} {p.intervention} started {start}; age after the work, by year: "
          + " ".join(f"{ages[y]:.0f}" for y in window if y >= start + p.duration))
    print(f"  ten-year reduction: asset ages again ${sum(aging.values()):,.0f}k, "
          f"frozen after the work ${sum(frozen.values()):,.0f}k, "
          f"overstated by {sum(frozen.values()) / sum(aging.values()) - 1:.0%}")
