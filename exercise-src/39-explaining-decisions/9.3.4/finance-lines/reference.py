from __future__ import annotations


def proven(record: dict) -> bool:
    """Optimal by the solver's status, and no plan can beat it by more than rounding."""
    return record["status"] == "OPTIMAL" and abs(record["bound"] - record["npv"]) <= 0.5


def finance_text(record: dict) -> list[str]:
    """The finance version of a run: one line per year, oldest first, then the value and its proof."""
    lines = []
    for year in sorted(record["budget"]):
        budget, spend = round(record["budget"][year]), round(record["spend"][year])   # whole $k first
        if spend > budget:
            lines.append(f"{year}: spend {spend:,} of {budget:,}, OVER by {spend - budget:,}")
        else:
            lines.append(f"{year}: spend {spend:,} of {budget:,}, {budget - spend:,} left")
    if proven(record):
        lines.append(f"NPV ${record['npv']:,.0f}k, proven optimal")
    else:
        lines.append(f"NPV ${record['npv']:,.0f}k, not proven: no plan is worth more than ${record['bound']:,.0f}k")
    return lines


if __name__ == "__main__":
    run = {"budget": {2027: 11000}, "spend": {2027: 10850}, "npv": 30412.4, "bound": 30412.4, "status": "OPTIMAL"}
    print("\n".join(finance_text(run)))
