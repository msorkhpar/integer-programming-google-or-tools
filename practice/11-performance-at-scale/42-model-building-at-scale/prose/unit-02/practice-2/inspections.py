from __future__ import annotations

import random
import statistics
import time

import pandas as pd
from ortools.math_opt.python import mathopt


def build_slow(tasks: pd.DataFrame, options: pd.DataFrame, capacity: pd.DataFrame) -> mathopt.Model:
    """The team's builder: correct, and slow, because every lookup scans a whole table."""
    model = mathopt.Model(name="inspections")
    y = {}
    for _, o in options.iterrows():
        y[o.task, o.week] = model.add_binary_variable(name=f"y_{o.task}_{o.week}")
    for _, t in tasks.iterrows():
        weeks = options[options.task == t.task]["week"]                     # scans every option
        model.add_linear_constraint(mathopt.LinearExpression() + sum(y[t.task, w] for w in weeks) <= 1,
                                    name=f"once_{t.task}")
    for _, c in capacity.iterrows():
        load = mathopt.LinearExpression()
        for _, o in options[options.week == c.week].iterrows():              # scans every option
            hours = tasks[tasks.task == o.task]["hours"].iloc[0]             # scans every task
            load += float(hours) * y[o.task, o.week]
        model.add_linear_constraint(load <= float(c.hours), name=f"crew_{c.week}")
    objective = mathopt.LinearExpression()
    for _, o in options.iterrows():
        objective += float(tasks[tasks.task == o.task]["value"].iloc[0]) * y[o.task, o.week]
    model.maximize(objective)
    return model


def build_fast(tasks: pd.DataFrame, options: pd.DataFrame, capacity: pd.DataFrame) -> mathopt.Model:
    """The same model as build_slow, built with lookups made once."""
    # TODO: build exactly build_slow's model, without scanning a table inside a loop.
    return mathopt.Model(name="inspections")


def instance(n: int, seed: int = 1) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """A made-up instance: n one-week inspection tasks, each allowed in up to three of 12 weeks."""
    draw = random.Random(seed)
    tasks = pd.DataFrame({"task": [f"T{i:04d}" for i in range(n)],
                          "hours": [draw.randint(4, 40) for _ in range(n)],
                          "value": [draw.randint(1, 90) for _ in range(n)]})
    rows = [(t, w) for t in tasks["task"] for w in sorted(draw.sample(range(1, 13), draw.randint(1, 3)))]
    options = pd.DataFrame(rows, columns=["task", "week"])
    capacity = pd.DataFrame({"week": range(1, 13), "hours": [draw.randint(200, 900) for _ in range(12)]})
    return tasks, options, capacity


if __name__ == "__main__":
    tasks, options, capacity = instance(1_500)
    same = build_fast(tasks, options, capacity).export_model() == build_slow(tasks, options, capacity).export_model()
    print("identical models:", same)
    ratios = []
    for _ in range(3):
        start = time.perf_counter()
        build_slow(tasks, options, capacity)
        slow = time.perf_counter() - start
        start = time.perf_counter()
        build_fast(tasks, options, capacity)
        ratios.append(slow / (time.perf_counter() - start))
    print(f"build_fast is {statistics.median(ratios):.0f}x faster on 1,500 tasks (median of 3 rounds; "
          "your machine's number will differ)")
