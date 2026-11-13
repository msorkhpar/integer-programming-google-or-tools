from __future__ import annotations


def solve_with_fallback(model, solvers: list[dict], gpu: bool):
    """Try each solver in order and return (the first Optimal result or None, what happened to each).

    A solver is {"name": str, "needs_gpu": bool, "solve": callable(model) -> dict with a "status"}.
    """
    log = []
    for solver in solvers:
        if solver["needs_gpu"] and not gpu:
            log.append(f"{solver['name']}: skipped (no GPU)")
            continue
        try:
            result = solver["solve"](model)
        except Exception:
            log.append(f"{solver['name']}: error")
            continue
        log.append(f"{solver['name']}: {result['status']}")
        if result["status"] == "Optimal":
            return result, log
    return None, log


if __name__ == "__main__":
    cpu = {"name": "cpu", "needs_gpu": False, "solve": lambda m: {"status": "Optimal", "objective": 1.0}}
    print(solve_with_fallback(None, [cpu], gpu=False))
