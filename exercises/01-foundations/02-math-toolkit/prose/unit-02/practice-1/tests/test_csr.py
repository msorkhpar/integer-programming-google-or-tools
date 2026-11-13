from csr import to_csr

# A water network's pumping rules: rows are stations, columns are pumps.


def test_triplets_in_row_order_become_csr():
    triplets = [(0, 0, 4), (0, 2, 1), (1, 1, 3), (2, 0, 2), (2, 3, 6)]
    indptr, indices, data = to_csr(3, triplets)
    assert indptr == [0, 2, 3, 5]
    assert indices == [0, 2, 1, 0, 3]
    assert data == [4, 1, 3, 2, 6]


def test_triplets_in_any_order_are_sorted_by_row_then_column():
    triplets = [(2, 3, 6), (0, 2, 1), (1, 1, 3), (2, 0, 2), (0, 0, 4)]
    indptr, indices, data = to_csr(3, triplets)
    assert indptr == [0, 2, 3, 5]
    assert indices == [0, 2, 1, 0, 3]
    assert data == [4, 1, 3, 2, 6]


def test_an_empty_row_repeats_its_pointer():
    triplets = [(0, 1, 7), (2, 0, 5)]                 # station 1 has no rule terms
    indptr, indices, data = to_csr(3, triplets)
    assert indptr == [0, 1, 1, 2]
    assert indices == [1, 0]
    assert data == [7, 5]


def test_empty_rows_at_the_end_still_get_pointers():
    triplets = [(0, 0, 1), (1, 2, -1)]                # stations 2 and 3 have no terms yet
    indptr, indices, data = to_csr(4, triplets)
    assert indptr == [0, 1, 2, 2, 2]
    assert indices == [0, 2]
    assert data == [1, -1]


def test_two_triplets_for_one_entry_are_added():
    triplets = [(0, 1, 2.5), (1, 0, 4.0), (0, 1, 1.5)]  # two rules both add to pump 1 at station 0
    indptr, indices, data = to_csr(2, triplets)
    assert indptr == [0, 1, 2]
    assert indices == [1, 0]
    assert data == [4.0, 4.0]
