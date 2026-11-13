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


def hours_out(f: Feeder) -> float:
    return f.switch_share * f.switch_hours + (1 - f.switch_share) * f.repair_hours


def consequence(f: Feeder) -> float:
    """The cost of one failure of the feeder, $k."""
    per_hour = f.residential * f.residential_cost + f.critical * f.critical_cost
    return f.repair_cost + per_hour * hours_out(f)


def saidi_minutes(f: Feeder, customers_served: int) -> float:
    """Minutes one failure of the feeder adds to the company's SAIDI."""
    return (f.residential + f.critical) * hours_out(f) * 60 / customers_served


if __name__ == "__main__":
    f = Feeder(1_800, 40, 0.6, 1.5, 8.0, 0.02, 0.5, 150)
    print(consequence(f), saidi_minutes(f, 90_000))
