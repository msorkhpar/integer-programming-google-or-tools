from __future__ import annotations


def relaxation_changes(values: dict[str, float], tol: float = 1e-6) -> list[str]:
    """Sorted lines, one per artificial variable of a feasibility relaxation that took a value."""
    # TODO: match each name against the four prefixes (with their underscore), skip small values.
    return ["nothing changed"]


if __name__ == "__main__":
    print(relaxation_changes({"route_7": 1.0, "ArtN_seats_bus3": 4.0, "ArtP_cover_north": 1.0}))
