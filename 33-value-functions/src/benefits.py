"""Benefit measures for GridCap projects: reliability, safety, environmental and financial.

GridCap is a fictional utility. The consequence table below (customers cut off, restoration time,
safety and emissions per failure) is invented for this module, like every other GridCap number.
"""

from __future__ import annotations

from dataclasses import dataclass

from gridcap import Portfolio, Project

#: The customers GridCap serves: the denominator of SAIDI and SAIFI (invented, like GridCap).
CUSTOMERS_SERVED = 600_000
#: Benefits are counted over this many years from the plan's first year.
EVALUATION_YEARS = 10
#: A sustained interruption lasts longer than this many minutes; shorter ones are momentary.
SUSTAINED_MINUTES = 5

#: How much younger an intervention makes its asset: it becomes (1 - depth) times as old.
DEPTH = {"replace": 1.0, "rebuild": 1.0, "underground": 1.0, "clear": 0.8, "widen": 0.8,
         "repair": 0.5, "trim": 0.5}


@dataclass(frozen=True)
class Consequence:
    """What one failure of an asset of this kind does, besides its repair bill."""

    customers: int        # customers interrupted
    minutes: int          # minutes until they are restored
    incidents: float      # expected public-safety incidents (contact, ignition, explosion)
    tco2e: float          # tonnes of CO2-equivalent released (fire, SF6 leak, oil fire)


CONSEQUENCE = {
    "line": Consequence(9_000, 120, 0.05, 2.0),
    "tower": Consequence(12_000, 240, 0.08, 1.0),
    "breaker": Consequence(6_000, 90, 0.03, 8.0),
    "transformer": Consequence(4_000, 300, 0.06, 15.0),
    "pole": Consequence(400, 360, 0.10, 0.5),
    "feeder": Consequence(1_500, 180, 0.04, 0.5),
    "circuit": Consequence(1_200, 150, 0.15, 25.0),
    "corridor": Consequence(7_000, 200, 0.20, 40.0),
}


@dataclass(frozen=True)
class Outage:
    customers: int
    minutes: float


def reliability_indices(outages: list[Outage], customers_served: int) -> dict[str, float]:
    """SAIFI, SAIDI and CAIDI of a year's outage log; momentary outages do not count."""
    sustained = [o for o in outages if o.minutes > SUSTAINED_MINUTES]
    interruptions = sum(o.customers for o in sustained)
    customer_minutes = sum(o.customers * o.minutes for o in sustained)
    saifi = interruptions / customers_served
    saidi = customer_minutes / customers_served
    return {"SAIFI": saifi, "SAIDI": saidi, "CAIDI": saidi / saifi if saifi else 0.0}


def failures(age: float, beta: float, eta: float, years: float) -> float:
    """Expected failures between ages `age` and `age + years` (Weibull, minimal repair)."""
    return ((age + years) / eta) ** beta - (age / eta) ** beta


def failures_avoided(portfolio: Portfolio, project: Project, start: int) -> float:
    """Expected failures the project avoids from its start to the end of the evaluation window."""
    asset = portfolio.asset(project.asset_id)
    first = portfolio.years[0]
    age = asset.age + (start - first)                  # the asset ages while it waits
    years = first + EVALUATION_YEARS - start            # benefit years left in the window
    after = (1 - DEPTH[project.intervention]) * age
    return (failures(age, asset.weibull_beta, asset.weibull_eta, years)
            - failures(after, asset.weibull_beta, asset.weibull_eta, years))


@dataclass(frozen=True)
class Measures:
    """One project's benefits, started in one year, each in its own unit."""

    failures: float           # expected failures avoided
    interruptions: float      # customer interruptions avoided (CI)
    customer_minutes: float   # customer minutes of interruption avoided (CMI)
    incidents: float          # expected safety incidents avoided
    tco2e: float              # tonnes CO2e avoided
    npv: int                  # net present value, $k

    @property
    def saifi(self) -> float:
        """The cut in SAIFI, summed over the window: interruptions per customer served."""
        return self.interruptions / CUSTOMERS_SERVED

    @property
    def saidi(self) -> float:
        """The cut in SAIDI, summed over the window: minutes per customer served."""
        return self.customer_minutes / CUSTOMERS_SERVED


def measures(portfolio: Portfolio, project: Project, start: int) -> Measures:
    f = failures_avoided(portfolio, project, start)
    c = CONSEQUENCE[portfolio.asset(project.asset_id).kind]
    return Measures(failures=f, interruptions=f * c.customers, customer_minutes=f * c.customers * c.minutes,
                    incidents=f * c.incidents, tco2e=f * c.tco2e, npv=project.npv[start])


def earliest_measures(portfolio: Portfolio) -> dict[str, Measures]:
    """Every project's measures if it starts as early as it can."""
    return {p.project_id: measures(portfolio, p, p.earliest_start) for p in portfolio.projects}
