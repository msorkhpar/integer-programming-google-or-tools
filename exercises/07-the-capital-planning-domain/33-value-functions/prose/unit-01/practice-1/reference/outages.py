from __future__ import annotations

from dataclasses import dataclass

SUSTAINED_OVER = 5   # minutes: a customer back on supply within this is a momentary interruption


@dataclass(frozen=True)
class Step:
    customers: int    # customers put back on supply in this step
    minute: float     # minutes after the outage began


def indices(outages: list[list[Step]], customers_served: int) -> dict[str, float]:
    """SAIFI, SAIDI and CAIDI of a year of outages, each restored in steps."""
    interruptions = 0
    customer_minutes = 0.0
    for steps in outages:
        for step in steps:
            if step.minute > SUSTAINED_OVER:
                interruptions += step.customers
                customer_minutes += step.customers * step.minute
    saifi = interruptions / customers_served
    saidi = customer_minutes / customers_served
    caidi = customer_minutes / interruptions if interruptions else 0.0
    return {"SAIFI": saifi, "SAIDI": saidi, "CAIDI": caidi}


if __name__ == "__main__":
    storm = [Step(600, 30), Step(400, 90)]
    print(indices([storm], 10_000))
