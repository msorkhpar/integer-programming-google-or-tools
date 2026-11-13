from __future__ import annotations


def proven(record: dict) -> bool:
    """Optimal by the solver's status, and no plan can beat it by more than rounding."""
    # TODO
    return False


def finance_text(record: dict) -> list[str]:
    """The finance version of a run: one line per year, oldest first, then the value and its proof."""
    # TODO: every number from the record.
    return []

if __name__ == "__main__":
    run = {"budget": {2027: 11000}, "spend": {2027: 10850}, "npv": 30412.4, "bound": 30412.4, "status": "OPTIMAL"}
    print("\n".join(finance_text(run)))
