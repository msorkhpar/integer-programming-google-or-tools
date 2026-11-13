import pandas as pd

from inspections import build_fast, build_slow, instance


def same(tasks, options, capacity) -> bool:
    return build_fast(tasks, options, capacity).export_model() == build_slow(tasks, options, capacity).export_model()


TASKS = pd.DataFrame({"task": ["T1", "T2", "T3", "T4"], "hours": [8, 12, 5, 20], "value": [30, 45, 10, 70]})
OPTIONS = pd.DataFrame({"task": ["T1", "T1", "T2", "T2", "T3", "T4"], "week": [1, 2, 2, 3, 1, 3]})
CAPACITY = pd.DataFrame({"week": [1, 2, 3], "hours": [20, 15, 25]})


def test_the_fast_builder_exports_the_slow_builders_model():
    assert same(TASKS, OPTIONS, CAPACITY)
    assert build_fast(TASKS, OPTIONS, CAPACITY).get_num_variables() == 6


def test_a_week_no_task_can_use_still_gets_its_capacity_row():
    capacity = pd.DataFrame({"week": [1, 2, 3, 4], "hours": [20, 15, 25, 30]})
    assert same(TASKS, OPTIONS, capacity)
    assert build_fast(TASKS, OPTIONS, capacity).get_num_linear_constraints() == 8


def test_capacity_rows_keep_the_order_of_the_capacity_table():
    capacity = pd.DataFrame({"week": [3, 1, 2], "hours": [25, 20, 15]})
    assert same(TASKS, OPTIONS, capacity)
    assert build_fast(TASKS, OPTIONS, capacity).get_num_linear_constraints() == 7


def test_a_task_with_no_allowed_week_still_gets_its_once_row():
    tasks = pd.concat([TASKS, pd.DataFrame({"task": ["T5"], "hours": [9], "value": [12]})], ignore_index=True)
    assert same(tasks, OPTIONS, CAPACITY)
    assert build_fast(tasks, OPTIONS, CAPACITY).get_num_linear_constraints() == 8


def test_variables_follow_the_order_of_the_options_table():
    options = OPTIONS.iloc[[4, 0, 5, 2, 1, 3]].reset_index(drop=True)
    assert same(TASKS, options, CAPACITY)
    assert build_fast(TASKS, options, CAPACITY).get_num_variables() == 6


def test_a_generated_instance_of_200_tasks_gives_the_same_model():
    tasks, options, capacity = instance(200, seed=3)
    assert same(tasks, options, capacity)
