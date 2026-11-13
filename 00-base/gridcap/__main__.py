"""Write a GridCap portfolio to disk.

    python -m gridcap tiny --out data/tiny            # CSV files
    python -m gridcap medium --seed 11 --json out.json
    python -m gridcap small --hash                    # print the content hash only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import SIZES, generate, save_csv
from .generator import DEFAULT_SEED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m gridcap", description=__doc__.splitlines()[0])
    parser.add_argument("size", choices=list(SIZES))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", help="folder for the CSV files")
    parser.add_argument("--json", help="file for the canonical JSON")
    parser.add_argument("--hash", action="store_true", help="print the content hash")
    args = parser.parse_args(argv)
    portfolio = generate(args.size, args.seed)
    if args.out:
        save_csv(portfolio, args.out)
    if args.json:
        Path(args.json).write_text(portfolio.to_json() + "\n", encoding="utf-8")
    if args.hash or not (args.out or args.json):
        print(portfolio.content_hash())
    return 0


if __name__ == "__main__":
    sys.exit(main())
