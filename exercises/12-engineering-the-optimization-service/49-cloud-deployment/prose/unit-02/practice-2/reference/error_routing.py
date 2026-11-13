from __future__ import annotations


def matches(names: list[str], error: str) -> bool:
    """Whether an ErrorEquals list names `error`, with the two wildcards."""
    return any(name == error or name == "States.ALL"
               or (name == "States.TaskFailed" and error != "States.Timeout") for name in names)


def route(state: dict, errors: list[str]) -> list[str]:
    """What the Task state does when its attempts fail with `errors`, in order, and the next one succeeds."""
    used = [0] * len(state.get("Retry", []))
    actions = []
    for error in errors:
        retriers = [i for i, r in enumerate(state.get("Retry", [])) if matches(r["ErrorEquals"], error)]
        if retriers:
            i = retriers[0]
            if used[i] < state["Retry"][i].get("MaxAttempts", 3):
                used[i] += 1
                actions.append("retry")
                continue
        catcher = next((c for c in state.get("Catch", []) if matches(c["ErrorEquals"], error)), None)
        actions.append(f"catch:{catcher['Next']}" if catcher else "fail")
        return actions
    return actions + ["succeeded"]
