"""Four changes run against the golden file, and what the comparison says about each.

GridCap is a fictional utility's portfolio. Each change is made in memory; the golden file is only
read. A record that matches prints PASS; one that does not prints FAIL and its first diff lines.
"""

from __future__ import annotations

import json
from dataclasses import replace

from bugs import broken
from golden import TOLERANCE, compare, load, result, scenarios
from plan_model import optimize


def show(title: str, records: dict, golden: dict, limit: int = 4) -> None:
    print(title)
    for name, record in records.items():
        found = compare(golden[name], record)
        print(f"  {'PASS' if not found else 'FAIL'} {name}")
        for line in found[:limit]:
            print("       " + line)
        if len(found) > limit:
            print(f"       ... {len(found) - limit} more")


def main() -> None:
    golden, cases = load(), scenarios()
    print("the golden record of one scenario, as stored:")
    print(json.dumps({"two equal projects, room for one": golden["two equal projects, room for one"]},
                     indent=1, sort_keys=True))
    show("1. A model bug: precedence ignores the lag",
         {name: result(p, broken("precedence ignores the lag")) for name, p in cases.items()}, golden)
    show("2. A model bug: precedence adds 1 to the lag",
         {name: result(p, broken("precedence adds 1 to the lag")) for name, p in cases.items()}, golden)
    small = cases["small"]
    moved = replace(small, budget={**small.budget, 2031: small.budget[2031] - 500})
    show("3. The data moved: GridCap small's 2031 budget lowered by 500", {"small": result(moved)}, golden)
    tie = cases["two equal projects, room for one"]
    flipped = replace(tie, projects=tuple(reversed(tie.projects)))
    show("4. The same data, its rows read in another order",
         {"two equal projects, room for one": result(flipped)}, golden)
    _, raw, _ = optimize(small, broken("must-do written as <="))
    print(f"solver noise: HiGHS returned {raw!r} for a plan whose NPV is {round(raw):,}; "
          f"equal as floats: {raw == round(raw)}; within {TOLERANCE['objective']}: "
          f"{abs(raw - round(raw)) <= TOLERANCE['objective']}")


if __name__ == "__main__":
    main()
