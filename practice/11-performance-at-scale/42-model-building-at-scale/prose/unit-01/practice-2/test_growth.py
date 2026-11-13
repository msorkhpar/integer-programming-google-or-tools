import math

import pytest

from growth import fit, predict


def test_an_exact_power_law_gives_back_its_exponent_and_constant():
    sizes = [100, 200, 400, 800]
    seconds = [3e-6 * n ** 2 for n in sizes]
    a, c = fit(sizes, seconds)
    assert a == pytest.approx(2.0)
    assert c == pytest.approx(3e-6)
    assert predict(sizes, seconds, 1_600) == pytest.approx(3e-6 * 1_600 ** 2)


def test_every_point_counts_not_only_the_two_ends():
    sizes = [1_000, 2_000, 4_000, 8_000]
    seconds = [1.0, 3.0, 3.0, 8.0]
    xs = [math.log(n) for n in sizes]
    ys = [math.log(t) for t in seconds]
    mx, my = sum(xs) / 4, sum(ys) / 4
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    assert fit(sizes, seconds)[0] == pytest.approx(slope)
    assert fit(sizes, seconds)[0] != pytest.approx(math.log(8.0) / math.log(8))


def test_the_order_of_the_measurements_does_not_matter():
    sizes, seconds = [4_000, 1_000, 8_000, 2_000], [3.0, 1.0, 8.0, 3.0]
    a, c = fit(sizes, seconds)
    b, d = fit([1_000, 2_000, 4_000, 8_000], [1.0, 3.0, 3.0, 8.0])
    assert (a, c) == (pytest.approx(b), pytest.approx(d))
    assert a == pytest.approx(0.9)


def test_the_prediction_follows_the_fitted_line_not_the_last_point():
    sizes, seconds = [1_000, 2_000, 4_000], [1.0, 1.5, 5.0]
    a, c = fit(sizes, seconds)
    assert predict(sizes, seconds, 8_000) == pytest.approx(c * 8_000 ** a)
    assert predict(sizes, seconds, 8_000) != pytest.approx(5.0 * 2 ** a)
    assert 9.0 < predict(sizes, seconds, 8_000) < 10.5

