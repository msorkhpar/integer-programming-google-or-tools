import pytest

from activity import csr_activity

# Warehouse picking rules: rows are aisles' capacity rules, columns are orders.
#   row 0: 2 x0 + 1 x3
#   row 1: 4 x1
#   row 2: 1 x0 + 3 x2 + 5 x3
INDPTR = [0, 2, 3, 6]
INDICES = [0, 3, 1, 0, 2, 3]
DATA = [2.0, 1.0, 4.0, 1.0, 3.0, 5.0]


def test_with_every_order_at_one_each_row_sums_its_values():
    assert csr_activity(INDPTR, INDICES, DATA, [1.0, 1.0, 1.0, 1.0]) == pytest.approx([3.0, 4.0, 9.0])


def test_each_value_multiplies_the_variable_of_its_column():
    x = [2.0, 0.0, 1.0, 3.0]
    assert csr_activity(INDPTR, INDICES, DATA, x) == pytest.approx([7.0, 0.0, 20.0])


def test_an_empty_row_has_activity_zero_in_its_place():
    indptr = [0, 1, 1, 3]                             # row 1 has no entries
    indices = [2, 0, 1]
    data = [3.0, 2.0, -1.0]
    assert csr_activity(indptr, indices, data, [1.0, 1.0, 1.0]) == pytest.approx([3.0, 0.0, 1.0])
