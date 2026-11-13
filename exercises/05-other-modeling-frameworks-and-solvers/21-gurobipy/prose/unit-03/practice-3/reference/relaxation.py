from __future__ import annotations

KINDS = {"ArtP_": "short by", "ArtN_": "over by", "ArtL_": "below its lower bound by",
         "ArtU_": "above its upper bound by"}


def relaxation_changes(values: dict[str, float], tol: float = 1e-6) -> list[str]:
    """Sorted lines, one per artificial variable of a feasibility relaxation that took a value."""
    lines = []
    for name, value in values.items():
        for prefix, words in KINDS.items():
            if name.startswith(prefix) and value > tol:
                lines.append(f"{name[len(prefix):]}: {words} {value:g}")
    return sorted(lines)


if __name__ == "__main__":
    print(relaxation_changes({"route_7": 1.0, "ArtN_seats_bus3": 4.0, "ArtP_cover_north": 1.0}))
