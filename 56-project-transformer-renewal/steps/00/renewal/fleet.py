"""The transformer fleet: one record per unit, and a seeded generator of fictional fleets.

The fleets are invented. They belong to GridCap, the course's fictional utility, and no number in
them comes from a real utility.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

FIRST_YEAR = 2027
REGIONS = ("north", "south", "east", "west")


@dataclass(frozen=True)
class Kind:
    share: float                 # share of the fleet
    cost: tuple[int, int]        # replacement cost range, $k
    beta: float                  # Weibull shape of the kind's failure curve
    eta: float                   # Weibull scale, years
    crew_weeks: int              # crew-weeks one replacement takes
    lead_years: int              # years from order to delivery of a new unit


KINDS = {
    "small": Kind(0.6, (250, 450), 3.2, 55.0, 2, 0),
    "medium": Kind(0.3, (700, 1300), 3.6, 60.0, 4, 1),
    "large": Kind(0.1, (2200, 3800), 4.0, 65.0, 8, 3),
}


@dataclass(frozen=True)
class Transformer:
    tid: str            # "T00042"
    substation: str     # "S007"
    region: str         # one of REGIONS
    kind: str           # a key of KINDS
    age: int            # years, in FIRST_YEAR
    cost: int           # $k to replace it
    cof: int            # $k, the cost of one failure
    condition: int      # 0-100 condition score from inspections; higher is worse
    pof: float          # probability it fails in FIRST_YEAR, from the asset-health team


def _pof(age: float, beta: float, eta: float) -> float:
    """Weibull probability of failing within a year, given working at `age` (lesson 7.3.1)."""
    return 1 - math.exp((age / eta) ** beta - ((age + 1) / eta) ** beta)


def generate_fleet(n: int, seed: int = 2027) -> list[Transformer]:
    """`n` fictional transformers in substations of 3 to 14 units; the same seed, the same fleet."""
    rng = random.Random(seed)
    fleet: list[Transformer] = []
    substation = 0
    while len(fleet) < n:
        substation += 1
        region = REGIONS[rng.randrange(len(REGIONS))]
        for _ in range(min(rng.randint(3, 14), n - len(fleet))):
            kind = rng.choices(list(KINDS), weights=[k.share for k in KINDS.values()])[0]
            k = KINDS[kind]
            age = rng.randint(3, 68)
            cost = 10 * round(rng.uniform(*k.cost) / 10)
            customers = rng.randint(200, 6000)
            fleet.append(Transformer(
                tid=f"T{len(fleet) + 1:05d}", substation=f"S{substation:04d}", region=region, kind=kind,
                age=age, cost=cost, cof=10 * round((1.5 * cost + 1.2 * customers) / 10),
                condition=max(0, min(100, round(100 * age / 70 + rng.gauss(0, 12)))),
                pof=round(_pof(age, k.beta, k.eta), 5)))
    return fleet


def risk(t: Transformer) -> float:
    """This year's expected failure cost, $k: PoF times CoF (lesson 7.3.3)."""
    return t.pof * t.cof
