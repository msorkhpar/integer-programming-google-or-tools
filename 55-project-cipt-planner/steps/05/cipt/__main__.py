"""python -m cipt EXPORT.json: plan the export and print the report."""

from __future__ import annotations

import argparse

from .data import read_request
from .report import render
from .solve import solve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cipt", description="Plan a capital portfolio.")
    parser.add_argument("export", help="the planning export, a JSON file")
    args = parser.parse_args(argv)
    request = read_request(args.export)
    print(render(request, solve(request)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
