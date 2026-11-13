from __future__ import annotations


def lock_refusal(plan_id: str, plans: dict[str, dict]) -> str | None:
    """Why `plan_id` may not become the program of record now, or None when it may."""
    p = plans[plan_id]
    if p["state"] != "Reviewed":
        return f"{plan_id} is {p['state']}, not Reviewed"
    if p["run"] is None or p["run"]["inputs_hash"] != p["inputs_hash"]:
        return f"{plan_id} has no run on its current inputs"
    if p["run"]["status"] != "OPTIMAL":
        return f"{plan_id}'s run is {p['run']['status']}"
    for other_id, other in plans.items():
        if other_id != plan_id and other["year"] == p["year"] and other["state"] == "Locked":
            return f"{p['year']} already has a program of record: {other_id}"
    return None


if __name__ == "__main__":
    plans = {"D-1": {"year": 2028, "state": "Reviewed", "inputs_hash": "a1",
                     "run": {"inputs_hash": "a1", "status": "OPTIMAL"}}}
    print(lock_refusal("D-1", plans))
