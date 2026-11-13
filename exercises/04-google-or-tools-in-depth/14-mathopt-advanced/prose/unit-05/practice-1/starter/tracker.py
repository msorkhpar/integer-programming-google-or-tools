from __future__ import annotations

from ortools.math_opt.python import mathopt


def make_tracker(objective: dict, maximize: bool):
    """(callback for MIP_SOLUTION, history of the best objective value after each reported solution)."""
    history: list[float] = []

    def callback(data: mathopt.CallbackData) -> mathopt.CallbackResult:
        # TODO: this solution's value, then the best so far, appended to history.
        return mathopt.CallbackResult()

    return callback, history


if __name__ == "__main__":
    model = mathopt.Model()
    a = model.add_binary_variable(name="a")
    callback, history = make_tracker({a: 3.0}, maximize=True)
    callback(mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION, solution={a: 1.0}))
    print(history)
