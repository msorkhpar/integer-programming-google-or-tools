from handoff import build

# A hospital courier's two cars: samples picked up at clinics and taken to labs.
DISTANCE = [
    [0, 5, 6, 9, 8, 7],
    [5, 0, 7, 4, 6, 9],
    [6, 7, 0, 8, 9, 4],
    [9, 4, 8, 0, 5, 6],
    [8, 6, 9, 5, 0, 3],
    [7, 9, 4, 6, 3, 0],
]
PAIRS = [(1, 4), (2, 5)]   # clinic 1's samples go to lab 4, clinic 2's to lab 5


def allowed(routes):
    manager, routing = build(DISTANCE, 2, PAIRS)
    return routing.ReadAssignmentFromRoutes(routes, True) is not None


def test_a_car_picks_up_before_it_delivers():
    assert allowed([[1, 4, 3], [2, 5]]) is True
    assert allowed([[4, 1, 3], [2, 5]]) is False


def test_one_car_carries_a_sample_from_clinic_to_lab():
    assert allowed([[1, 4, 3], [2, 5]]) is True
    # Clinic 1 by car 0 (5 km into its route), lab 4 by car 1 (13 km into its route).
    assert allowed([[1, 3], [2, 5, 4]]) is False
