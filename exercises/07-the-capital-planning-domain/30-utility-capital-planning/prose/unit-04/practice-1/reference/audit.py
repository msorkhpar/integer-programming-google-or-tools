from __future__ import annotations


def audit(original: dict, replay: dict, tol: float = 1e-6) -> list[str]:
    """What a replay of a stored run did not reproduce; an empty list means it reproduced."""
    if original["snapshot"] != replay["snapshot"]:
        return ["inputs differ"]
    findings = []
    settings = sorted(k for k in set(original["settings"]) | set(replay["settings"])
                      if original["settings"].get(k) != replay["settings"].get(k))
    if settings:
        findings.append("settings differ: " + ", ".join(settings))
    if original["status"] != replay["status"]:
        findings.append("status differs")
    a, b = original["objective"], replay["objective"]
    if abs(a - b) > tol * max(1.0, abs(a)):
        findings.append("objective differs")
    plan_a, plan_b = original["plan"], replay["plan"]
    moved = sorted(i for i in set(plan_a) | set(plan_b) if plan_a.get(i) != plan_b.get(i))
    if moved:
        findings.append("plan differs: " + ", ".join(moved))
    return findings


if __name__ == "__main__":
    run = {"snapshot": "9a1c", "settings": {"threads": 1}, "status": "OPTIMAL", "objective": 812.0,
           "plan": {"W1": 2027, "W3": 2028}}
    print(audit(run, dict(run)))
    print(audit(run, {**run, "settings": {"threads": 8}, "plan": {"W1": 2027, "W3": 2029}}))
