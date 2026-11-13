from __future__ import annotations


def audit(original: dict, replay: dict, tol: float = 1e-6) -> list[str]:
    """What a replay of a stored run did not reproduce; an empty list means it reproduced."""
    # TODO: compare the two runs field by field. The finding below is a placeholder.
    return ["not audited"]


if __name__ == "__main__":
    run = {"snapshot": "9a1c", "settings": {"threads": 1}, "status": "OPTIMAL", "objective": 812.0,
           "plan": {"W1": 2027, "W3": 2028}}
    print(audit(run, dict(run)))
