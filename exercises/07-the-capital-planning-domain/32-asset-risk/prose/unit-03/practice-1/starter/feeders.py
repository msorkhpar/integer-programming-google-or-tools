from dataclasses import dataclass


@dataclass(frozen=True)
class Feeder:
    residential: int          # customers
    critical: int             # customers
    switch_share: float       # share of the customers switched to another feeder
    switch_hours: float       # hours until the switching is done
    repair_hours: float       # hours until the feeder is repaired
    residential_cost: float   # $k per residential customer-hour
    critical_cost: float      # $k per critical customer-hour
    repair_cost: float        # $k, crew and parts


def consequence(f: Feeder) -> float:
    """The cost of one failure of the feeder, $k."""
    # TODO: repair plus each class's customers times its hourly cost times the average hours out.
    return 0.0


def saidi_minutes(f: Feeder, customers_served: int) -> float:
    """Minutes one failure of the feeder adds to the company's SAIDI."""
    # TODO: customer-minutes without power, per customer served.
    return 0.0


if __name__ == "__main__":
    f = Feeder(1_800, 40, 0.6, 1.5, 8.0, 0.02, 0.5, 150)
    print(consequence(f), saidi_minutes(f, 90_000))
