from progress import events, stopped_by_a_limit

# Made-up progress lines of a crew-rostering model (maximized), shaped like CP-SAT 9.15's.
FINISHED = """Preloading model.
#Bound   0.01s best:-inf  next:[300,9100] initial_domain

Starting search at 0.01s with 1 workers.
1 full problem subsolver: [main]

#Bound   0.02s best:-inf  next:[300,5200] main
#1       0.03s best:4100 next:[4101,5200] main
#2       0.05s best:4650 next:[4651,5200] main
#Bound   0.06s best:4650 next:[4651,4700] main
#3       0.08s best:4700 next:[4701,4700] main
#Done    0.09s main
"""

STOPPED = """#Bound   0.04s best:-inf  next:[10,800] main
#1       0.10s best:610 next:[611,800] main
#Bound   0.30s best:610 next:[611,760] main
"""


def test_each_progress_line_becomes_one_event():
    assert events(FINISHED) == [
        ("bound", None, 9100, "initial_domain"),
        ("bound", None, 5200, "main"),
        ("solution", 4100, 5200, "main"),
        ("solution", 4650, 5200, "main"),
        ("bound", 4650, 4700, "main"),
        ("solution", 4700, 4700, "main"),
        ("done", None, None, "main"),
    ]


def test_a_log_without_done_was_stopped_by_a_limit():
    assert stopped_by_a_limit(STOPPED) is True
    assert stopped_by_a_limit(FINISHED) is False


def test_the_worker_is_named_without_its_comment():
    line = "#Bound   0.01s best:-inf  next:[1827,27576] main (initial_propagation)\n"
    assert events(line) == [("bound", None, 27576, "main")]


def test_model_lines_are_not_events():
    log = STOPPED + "#Model   0.61s var:858/859 constraints:364/364\n#2       0.70s best:640 next:[641,760] main\n"
    assert events(log)[-1:] == [("solution", 640, 760, "main")]
    assert len(events(log)) == 4
