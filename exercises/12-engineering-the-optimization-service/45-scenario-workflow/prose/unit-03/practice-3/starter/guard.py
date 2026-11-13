from __future__ import annotations


def lock_refusal(plan_id: str, plans: dict[str, dict]) -> str | None:
    """Why `plan_id` may not become the program of record now, or None when it may."""
    # TODO
    return None


if __name__ == "__main__":
    plans = {"D-1": {"year": 2028, "state": "Reviewed", "inputs_hash": "a1",
                     "run": {"inputs_hash": "a1", "status": "OPTIMAL"}}}
    print(lock_refusal("D-1", plans))
