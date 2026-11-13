from __future__ import annotations


def solve_with_fallback(model, solvers: list[dict], gpu: bool):
    """Try each solver in order and return (the first Optimal result or None, what happened to each).

    A solver is {"name": str, "needs_gpu": bool, "solve": callable(model) -> dict with a "status"}.
    """
    # TODO: skip GPU solvers without a GPU, survive a solver that raises, accept only "Optimal".
    return None, []

if __name__ == "__main__":
    cpu = {"name": "cpu", "needs_gpu": False, "solve": lambda m: {"status": "Optimal", "objective": 1.0}}
    print(solve_with_fallback(None, [cpu], gpu=False))
