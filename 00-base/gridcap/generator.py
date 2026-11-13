"""Generate a GridCap portfolio from a size and a seed.

The same size and seed give the same portfolio, byte for byte, on any machine: the generator draws
only `random.Random(seed).random()` and does its own integer arithmetic, so neither numpy's nor
Python's sampling helpers can change it between versions. `tests/test_generator.py` pins the
content hash of every size.
"""

from __future__ import annotations

import math
import random

from .portfolio import PROGRAMS, REGIONS, Asset, Portfolio, Project

#: name -> (projects, first year, years in the horizon)
SIZES = {
    "tiny": (8, 2027, 3),
    "small": (40, 2027, 5),
    "medium": (400, 2027, 10),
    "large": (10_000, 2027, 10),
}
DEFAULT_SEED = 2027
DISCOUNT_RATE = 0.07

_INTERVENTIONS = {
    "transmission": (("tower", "replace"), ("line", "rebuild"), ("breaker", "replace"), ("tower", "repair")),
    "distribution": (("transformer", "replace"), ("pole", "replace"), ("feeder", "underground"),
                     ("transformer", "repair")),
    "vegetation": (("circuit", "trim"), ("circuit", "clear"), ("corridor", "widen"), ("circuit", "trim")),
}
#: (capex low, capex high) in $k, by program
#: the tiny portfolio's programs, fixed so its structure reads well by hand
_TINY_PROGRAMS = ("distribution", "transmission", "transmission", "transmission", "vegetation",
                  "distribution", "distribution", "vegetation")
_CAPEX = {"transmission": (900, 6_000), "distribution": (300, 2_500), "vegetation": (80, 600)}


class _Draw:
    """Every random choice the generator makes, built on `random()` alone."""

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def unit(self) -> float:
        return self._rng.random()

    def below(self, n: int) -> int:
        return min(int(self.unit() * n), n - 1)

    def between(self, low: int, high: int) -> int:
        return low + self.below(high - low + 1)

    def pick(self, items):
        return items[self.below(len(items))]

    def chance(self, p: float) -> bool:
        return self.unit() < p


def generate(size: str = "tiny", seed: int = DEFAULT_SEED) -> Portfolio:
    """Build the GridCap portfolio of one size ("tiny", "small", "medium" or "large")."""
    if size not in SIZES:
        raise ValueError(f"unknown size {size!r}; choose one of {', '.join(SIZES)}")
    count, first, horizon = SIZES[size]
    years = tuple(range(first, first + horizon))
    draw = _Draw(seed * 1_000 + list(SIZES).index(size))
    width = max(3, len(str(count)))

    assets: list[Asset] = []
    projects: list[Project] = []
    # Structure first, so even the tiny portfolio has one of each relationship: project 2 is a
    # must-do, project 4 is the child of project 3, and projects 6 and 7 are alternatives
    # (repair or replace the same asset).
    index = 0
    while index < count:
        number = index + 1
        program = _TINY_PROGRAMS[index] if size == "tiny" else draw.pick(PROGRAMS)
        region = REGIONS[index % 4] if size == "tiny" else draw.pick(REGIONS)
        kind, intervention = draw.pick(_INTERVENTIONS[program])
        asset = _asset(draw, f"A{number:0{width}d}", kind, region)
        assets.append(asset)

        alternative = (size == "tiny" and number == 6) or (size != "tiny" and draw.chance(0.08))
        if alternative and index + 1 < count and kind != "circuit":
            pair = _alternatives(draw, years, program, region, asset, number, width)
            projects.extend(pair)
            index += 2
            continue
        projects.append(_project(draw, years, program, region, asset, intervention, number, width))
        index += 1

    projects = _relate(draw, size, projects)
    projects = [_with_npv(draw, p, years) for p in projects]
    return _limits(draw, size, seed, years, tuple(projects), tuple(assets))


def _asset(draw: _Draw, asset_id: str, kind: str, region: str) -> Asset:
    beta = round(1.5 + 2.5 * draw.unit(), 2)          # wear-out: shape above 1
    eta = round(25 + 35 * draw.unit(), 1)              # characteristic life, years
    age = draw.between(5, int(eta * 1.2))
    rul = max(1, int(eta - age + 8 * (draw.unit() - 0.5)))
    cof = draw.between(50, 4_000)
    return Asset(asset_id, kind, region, age, beta, eta, rul, cof)


def _profile(draw: _Draw, program: str, years: tuple[int, ...]) -> tuple[int, ...]:
    low, high = _CAPEX[program]
    capex = 10 * (draw.between(low, high) // 10)
    longest = 1 if program == "vegetation" else min(3, len(years) - 1)
    duration = draw.between(1, max(1, longest))
    if duration == 1:
        return (capex,)
    weights = [1 + draw.below(4) for _ in range(duration)]
    parts = [10 * (capex * w // (10 * sum(weights))) for w in weights]
    parts[-1] += capex - sum(parts)
    return tuple(parts)


def _window(draw: _Draw, years: tuple[int, ...], duration: int) -> tuple[int, int]:
    last_start = years[-1] - duration + 1
    earliest = years[0] + draw.below(max(1, last_start - years[0] + 1))
    latest = min(last_start, earliest + draw.below(4))
    return earliest, latest


def _name(asset: Asset, intervention: str, program: str) -> str:
    noun = {"line": "115 kV line", "tower": "tower set", "breaker": "breaker bay",
            "transformer": "substation transformer", "pole": "pole run", "feeder": "feeder segment",
            "circuit": "circuit", "corridor": "corridor"}[asset.kind]
    return f"{asset.region} {noun} {intervention} ({asset.asset_id})"


def _project(draw, years, program, region, asset, intervention, number, width, alt_group=None) -> Project:
    profile = _profile(draw, program, years)
    earliest, latest = _window(draw, years, len(profile))
    crew = max(1, sum(profile) // 400) if program != "vegetation" else 1 + draw.below(3)
    return Project(
        project_id=f"P{number:0{width}d}", name=_name(asset, intervention, program), program=program,
        region=region, asset_id=asset.asset_id, intervention=intervention, cost_profile=profile,
        earliest_start=earliest, latest_start=latest, must_do=False, parent=None, parent_lag=0,
        alt_group=alt_group, crew_months=crew,
    )


def _alternatives(draw, years, program, region, asset, number, width) -> list[Project]:
    group = f"G{number:0{width}d}"
    replace = _project(draw, years, program, region, asset, "replace", number, width, group)
    repair_cost = tuple(max(10, 10 * (c * 35 // 1000)) for c in replace.cost_profile[:1])
    repair = Project(
        project_id=f"P{number + 1:0{width}d}", name=_name(asset, "repair", program), program=program,
        region=region, asset_id=asset.asset_id, intervention="repair", cost_profile=repair_cost,
        earliest_start=years[0], latest_start=min(years[-1], years[0] + 1), must_do=False, parent=None,
        parent_lag=0, alt_group=group, crew_months=max(1, replace.crew_months // 3),
    )
    return [replace, repair]


def _relate(draw: _Draw, size: str, projects: list[Project]) -> list[Project]:
    """Mark must-dos and parent-child bundles."""
    out: list[Project] = []
    by_id = {p.project_id: p for p in projects}
    for i, p in enumerate(projects):
        must = (i == 1) if size == "tiny" else (p.alt_group is None and draw.chance(0.10))
        parent, lag = None, 0
        wants_parent = (i == 3) if size == "tiny" else draw.chance(0.10)
        if wants_parent and i > 0 and p.alt_group is None and not must:
            candidate = projects[i - 1]
            if candidate.alt_group is None and candidate.parent is None and \
                    candidate.earliest_start + 1 <= p.latest_start and out[i - 1].parent is None:
                parent = candidate.project_id
                lag = 0 if draw.chance(0.5) else 1
        p = _replace(p, must_do=must, parent=parent, parent_lag=lag)
        if parent is not None:
            # The child cannot start before its parent can (plus the lag).
            earliest = max(p.earliest_start, by_id[parent].earliest_start + lag)
            if earliest > p.latest_start:
                p = _replace(p, parent=None, parent_lag=0)
            else:
                p = _replace(p, earliest_start=earliest)
        out.append(p)
    return out


def _replace(p: Project, **changes) -> Project:
    data = {f: getattr(p, f) for f in p.__dataclass_fields__}
    data.update(changes)
    return Project(**data)


def _with_npv(draw: _Draw, p: Project, years: tuple[int, ...]) -> Project:
    """NPV by start year: the benefit stream discounted, less the discounted cost."""
    ratio = 1.15 + 0.9 * draw.unit()                   # benefit over cost, before discounting
    decay = 0.03 + 0.05 * draw.unit()                  # value lost per year of delay (risk carried)
    npv = {}
    for start in p.starts():
        shift = start - years[0]
        discount = (1 + DISCOUNT_RATE) ** -shift
        benefit = p.capex * ratio * discount * (1 - decay) ** (start - p.earliest_start)
        cost = sum(c * (1 + DISCOUNT_RATE) ** -(shift + k) for k, c in enumerate(p.cost_profile))
        npv[start] = int(math.floor(benefit - cost + 0.5))
    return _replace(p, npv=npv)


def _limits(draw, size, seed, years, projects, assets) -> Portfolio:
    total = sum(p.capex for p in projects)
    must = sum(p.capex for p in projects if p.must_do)
    capital_budget = max(must, 10 * (total * 55 // 1000))

    per_year: dict[int, int] = {}
    for y in years:
        per_year[y] = 10 * (int(total / len(years) * (0.50 + 0.15 * draw.unit())) // 10)
    # Must-do work started as early as it can must fit every year's budget.
    for p in projects:
        if p.must_do:
            for y, amount in p.spend(p.earliest_start).items():
                per_year[y] = max(per_year[y], amount)
    must_spend = {y: 0 for y in years}
    for p in projects:
        if p.must_do:
            for y, amount in p.spend(p.earliest_start).items():
                must_spend[y] += amount
    budget = {y: max(per_year[y], 10 * ((must_spend[y] * 12 // 10 + 9) // 10)) for y in years}

    region_total = {r: sum(p.capex for p in projects if p.region == r) for r in REGIONS}
    region_budget = {}
    region_must: dict = {}
    for r in REGIONS:
        share = region_total[r] / total if total else 0
        for y in years:
            region_budget[(r, y)] = 10 * (int(budget[y] * min(1.0, share * 1.6 + 0.05)) // 10)
    # Must-do work started as early as it can must fit its region's cap too, as it fits the year's.
    for p in projects:
        if p.must_do:
            for y, amount in p.spend(p.earliest_start).items():
                region_must[(p.region, y)] = region_must.get((p.region, y), 0) + amount
    for key, amount in region_must.items():
        region_budget[key] = max(region_budget[key], 10 * ((amount + 9) // 10))
    region_floor = {r: 10 * (int(region_total[r] * 0.20) // 10) for r in REGIONS}

    crew_need = {(prog, y): 0 for prog in PROGRAMS for y in years}
    for p in projects:
        for y in p.spend(p.earliest_start):
            crew_need[(p.program, y)] += p.crew_months
    crews = {k: max(2, int(v * 0.6) + 1) for k, v in crew_need.items()}

    return Portfolio(
        name=f"GridCap {size}", seed=seed, years=years, discount_rate=DISCOUNT_RATE,
        projects=projects, assets=assets, capital_budget=capital_budget, budget=budget,
        region_budget=region_budget, region_floor=region_floor, crews=crews,
    )
