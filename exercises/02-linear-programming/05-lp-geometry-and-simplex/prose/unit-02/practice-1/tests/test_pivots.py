from pivots import choose_pivot

START = [[1, 1, 1, 0, 0, 4],
         [1, 3, 0, 1, 0, 6],
         [1, 0, 0, 0, 1, 3],
         [-3, -2, 0, 0, 0, 0]]
SECOND = [[0, 1, 1, 0, -1, 1],
          [0, 3, 0, 1, -1, 3],
          [1, 0, 0, 0, 1, 3],
          [0, -2, 0, 0, 3, 9]]
FINAL = [[0, 1, 1, 0, -1, 1],
         [0, 0, -3, 1, 2, 0],
         [1, 0, 0, 0, 1, 3],
         [0, 0, 2, 0, 1, 11]]


def test_the_most_negative_column_enters_and_the_smallest_ratio_leaves():
    assert choose_pivot(START) == (2, 0)


def test_a_tableau_with_no_negative_objective_entry_is_optimal():
    assert choose_pivot(FINAL) is None


def test_rows_with_a_negative_entry_set_no_limit():
    T = [[-1, 1, 1, 0, 2],
         [1, 0, 0, 1, 5],
         [-4, -1, 0, 0, 0]]
    assert choose_pivot(T) == (1, 0)


def test_a_tie_in_the_ratio_test_goes_to_the_lowest_row():
    assert choose_pivot(SECOND) == (0, 1)
