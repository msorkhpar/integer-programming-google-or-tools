from relaxation import relaxation_changes


def test_row_violations_are_reported_as_short_or_over():
    values = {"ArtN_seats_bus3": 4.0, "ArtP_cover_north": 1.0, "ArtP_seats_bus3": 0.0}
    assert relaxation_changes(values) == ["cover_north: short by 1", "seats_bus3: over by 4"]


def test_bound_violations_are_reported():
    values = {"ArtU_drive_minutes": 12.5, "ArtL_stops_route2": 2.0}
    assert relaxation_changes(values) == ["drive_minutes: above its upper bound by 12.5",
                                          "stops_route2: below its lower bound by 2"]


def test_the_original_variables_are_not_changes():
    values = {"route_7": 1.0, "bus_3": 1.0, "ArtN_seats_bus3": 4.0}
    assert relaxation_changes(values) == ["seats_bus3: over by 4"]


def test_counting_binaries_are_not_changes():
    values = {"ArtNB_seats_bus3": 1.0, "ArtN_seats_bus3": 4.0, "ArtPB_cover_north": 1.0, "ArtUB_drive_minutes": 1.0}
    assert relaxation_changes(values) == ["seats_bus3: over by 4"]


def test_values_within_the_tolerance_are_not_changes():
    values = {"ArtN_seats_bus3": 4.0, "ArtP_cover_north": 1e-9, "ArtU_drive_minutes": 3e-7}
    assert relaxation_changes(values) == ["seats_bus3: over by 4"]
    assert relaxation_changes({"ArtP_cover_north": 0.01}, tol=0.1) == []
