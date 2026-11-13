from invoices import fits


def test_a_batch_within_the_budget_fits_and_one_over_it_does_not():
    assert fits([0.1, 0.2], 0.3) is True
    assert fits([0.1, 0.2, 0.05], 0.3) is False


def test_every_amount_becomes_the_nearest_cent():
    assert fits([0.29, 0.58], 0.87) is True
    assert fits([0.29, 0.58], 0.86) is False


def test_one_cent_over_is_over():
    assert fits([10.00, 0.01], 10.01) is True
    assert fits([10.00, 0.01], 10.00) is False
