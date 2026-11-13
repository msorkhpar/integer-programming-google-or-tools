"""The Valley inspection day: GridCap's Valley substations as a routing instance.

GridCap is fictional, and it has no coordinates. The sites are the substation transformers of the
medium portfolio's Valley region; everything spatial here (the map positions, the drive times) is
invented by this file from SEED, so the instance is the same on every run and describes no real
place. Times are whole minutes after 08:00, the start of the crews' shift.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from gridcap import generate

SEED = 52
SHIFT = 480                  # minutes, 08:00 to 16:00
MINUTES_PER_KM = 1.5         # 40 km/h on rural roads
URGENT_RUL = 5               # a transformer with at most 5 years of predicted life left is urgent


@dataclass(frozen=True)
class Site:
    name: str                    # the transformer's asset id, or "YARD" for the crews' depot
    x: float                     # km east of the map's corner (invented)
    y: float                     # km north of the map's corner (invented)
    service: int                 # minutes the inspection takes on site
    kits: int                    # oil-sample kits the inspection uses
    window: tuple[int, int]      # the arrival window, in minutes after 08:00
    urgent: bool                 # must be inspected today
    cof: int                     # the transformer's consequence of failure, $k


def sites(urgent_only: bool = False) -> list[Site]:
    """The yard first, then one site per Valley transformer, in asset-id order."""
    draw = random.Random(SEED)
    out = [Site("YARD", 15.0, 15.0, 0, 0, (0, SHIFT), True, 0)]
    transformers = [a for a in generate("medium").assets if a.kind == "transformer" and a.region == "Valley"]
    for number, asset in enumerate(transformers):
        x, y = round(draw.uniform(0, 30), 1), round(draw.uniform(0, 30), 1)
        service = 30 if asset.age < 20 else 45 if asset.age < 40 else 60
        kits = 1 if asset.age < 20 else 2 if asset.age < 40 else 3
        window = {0: (0, 180), 2: (240, 420)}.get(number % 4, (0, SHIFT))
        site = Site(asset.asset_id, x, y, service, kits, window, asset.rul <= URGENT_RUL, asset.cof)
        if site.urgent or not urgent_only:
            out.append(site)
    return out


def drive_minutes(places: list[Site]) -> list[list[int]]:
    """Whole minutes from each site to each other, rounded from the straight-line distance."""
    return [[round(MINUTES_PER_KM * math.dist((a.x, a.y), (b.x, b.y))) for b in places] for a in places]


def clock(minutes: int) -> str:
    """Minutes after 08:00 as a wall-clock time."""
    return f"{8 + minutes // 60:02d}:{minutes % 60:02d}"
