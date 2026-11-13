from ortools.math_opt.python import mathopt

from rows import describe, describe_model


def fleet():
    model = mathopt.Model(name="fleet")
    bus = model.add_integer_variable(lb=0, ub=30, name="bus")
    tram = model.add_integer_variable(lb=0, ub=12, name="tram")
    van = model.add_variable(lb=0, ub=50, name="van")
    return model, bus, tram, van


def test_an_upper_bounded_row_reads_as_less_or_equal():
    model, bus, tram, van = fleet()
    row = model.add_linear_constraint(4 * tram + 2.5 * bus <= 120, name="depot_space")
    assert describe(row) == "depot_space: 2.5 bus + 4 tram <= 120"


def test_every_row_of_a_model_is_described_in_creation_order():
    model, bus, tram, van = fleet()
    model.add_linear_constraint(4 * tram + 2.5 * bus <= 120, name="depot_space")
    model.add_linear_constraint(3 * van + 7 * bus <= 400, name="drivers")
    assert describe_model(model) == ["depot_space: 2.5 bus + 4 tram <= 120", "drivers: 7 bus + 3 van <= 400"]


def test_a_lower_bounded_row_reads_as_greater_or_equal():
    model, bus, tram, van = fleet()
    row = model.add_linear_constraint(60 * bus + 150 * tram >= 2400, name="seats")
    assert describe(row) == "seats: 60 bus + 150 tram >= 2400"


def test_an_equality_row_reads_with_two_equals_signs():
    model, bus, tram, van = fleet()
    row = model.add_linear_constraint(van == 2 * tram, name="feeders")
    assert describe(row) == "feeders: -2 tram + van == 0"


def test_a_ranged_row_shows_both_bounds():
    model, bus, tram, van = fleet()
    row = model.add_linear_constraint((10 <= bus + tram) <= 25, name="fleet_size")
    assert describe(row) == "fleet_size: 10 <= bus + tram <= 25"


def test_negative_and_unit_coefficients_read_naturally():
    model, bus, tram, van = fleet()
    row = model.add_linear_constraint(bus - 0.5 * van - tram <= 3, name="balance")
    assert describe(row) == "balance: bus - tram - 0.5 van <= 3"
