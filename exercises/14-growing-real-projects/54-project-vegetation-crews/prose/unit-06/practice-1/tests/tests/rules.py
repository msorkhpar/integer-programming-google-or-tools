"""The risk rule as the planner states it, written again here so the tests do not trust the code they test."""

DEFER_WEEKS = 26        # a circuit left untrimmed waits this many weeks past the season


def carried(row: dict, end: int) -> int:
    """$k of risk a circuit (an inventory row) carries over weeks 0 to end - 1: its weekly share of the
    yearly risk, plus `growth` more every week it waits (a row with no growth column does not grow)."""
    weekly = [row["risk"] / 52 + row.get("growth", 0) * week for week in range(end)]
    return round(sum(weekly))
