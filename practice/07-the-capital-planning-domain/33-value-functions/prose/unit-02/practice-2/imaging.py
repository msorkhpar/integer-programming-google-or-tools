from __future__ import annotations

from dataclasses import dataclass

#: For each measure, whether a higher level is better.
HIGHER_IS_BETTER = {"downtime_hours": False, "scans_per_day": True, "energy_mwh": False}


@dataclass(frozen=True)
class Replacement:
    name: str
    before: dict[str, float]      # each measure's level with the old machine
    after: dict[str, float]       # and with the new one


def improvement(measure: str, before: float, after: float) -> float:
    """How much better the measure gets: positive is better, 0 is no change."""
    # TODO
    return 0.0


def project_score(project: Replacement, reference: dict[str, float], weights: dict[str, float]) -> float:
    # TODO: this project's normalized, weighted improvement.
    return 0.0


def plan_score(plan: list[str], projects: dict[str, Replacement], reference: dict[str, float],
               weights: dict[str, float]) -> float:
    """The value of funding the projects named in `plan`."""
    return sum(project_score(projects[name], reference, weights) for name in plan)


if __name__ == "__main__":
    mri = Replacement("MRI", {"downtime_hours": 120, "scans_per_day": 20, "energy_mwh": 300},
                      {"downtime_hours": 30, "scans_per_day": 26, "energy_mwh": 240})
    reference = {"downtime_hours": 100, "scans_per_day": 10, "energy_mwh": 100}
    weights = {"downtime_hours": 0.5, "scans_per_day": 0.3, "energy_mwh": 0.2}
    print(plan_score(["MRI"], {"MRI": mri}, reference, weights))
