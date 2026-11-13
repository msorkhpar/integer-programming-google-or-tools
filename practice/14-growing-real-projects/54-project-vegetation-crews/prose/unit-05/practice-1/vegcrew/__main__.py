"""python -m vegcrew [tiny|small|medium] [--seed N]: plan a generated season and print the plan."""

from __future__ import annotations

import argparse

from vegcrew.data import season_from_dict
from vegcrew.generate import SIZES, scenario
from vegcrew.planner import make_plan
from vegcrew.report import format_plan


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="vegcrew")
    parser.add_argument("size", nargs="?", default="small", choices=sorted(SIZES))
    parser.add_argument("--seed", type=int, default=54)
    args = parser.parse_args(argv)
    season = season_from_dict(scenario(args.size, args.seed))
    print(format_plan(season, make_plan(season)))


if __name__ == "__main__":
    main()
