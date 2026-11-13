"""python -m vegcrew [tiny|small|medium] [--seed N] [--record]: plan a generated season and print the
plan, or with --record its record as canonical JSON."""

from __future__ import annotations

import argparse

from vegcrew.data import season_from_dict
from vegcrew.generate import SIZES, scenario
from vegcrew.planner import make_plan
from vegcrew.record import dumps, plan_record
from vegcrew.report import format_plan


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="vegcrew")
    parser.add_argument("size", nargs="?", default="small", choices=sorted(SIZES))
    parser.add_argument("--seed", type=int, default=54)
    parser.add_argument("--record", action="store_true", help="print the plan's record as JSON")
    args = parser.parse_args(argv)
    raw = scenario(args.size, args.seed)
    season = season_from_dict(raw)
    plan = make_plan(season)
    if args.record:
        print(dumps(plan_record(raw, plan)), end="")
    else:
        print(format_plan(season, plan))


if __name__ == "__main__":
    main()
