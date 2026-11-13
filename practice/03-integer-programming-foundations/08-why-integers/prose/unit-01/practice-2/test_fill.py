from fill import Project, round_down_and_fill


def test_the_whole_projects_are_kept_and_the_leftover_budget_is_filled():
    pipes = [Project("A", 50, 60, must_do=True), Project("B", 40, 52), Project("H", 30, 24), Project("F", 10, 9)]
    shares = {"A": 1.0, "B": 0.25, "H": 0.0, "F": 0.0}
    assert round_down_and_fill(shares, pipes, 100) == {"A", "B", "F"}


def test_a_share_a_hair_below_one_counts_as_funded_whole():
    pipes = [Project("A", 50, 60, must_do=True), Project("B", 40, 52), Project("N", 55, 68), Project("F", 10, 9)]
    shares = {"A": 0.9999999, "B": 1.0, "N": 0.0, "F": 0.0}
    assert round_down_and_fill(shares, pipes, 100) == {"A", "B", "F"}


def test_the_fill_walks_by_value_per_dollar_not_by_value():
    pipes = [Project("A", 50, 60, must_do=True), Project("K", 20, 30), Project("J", 45, 50),
             Project("L", 25, 35), Project("M", 25, 31)]
    shares = {"A": 1.0, "K": 1.0, "L": 0.2, "J": 0.0, "M": 0.0}
    assert round_down_and_fill(shares, pipes, 120) == {"A", "K", "L", "M"}


def test_a_child_is_not_added_while_its_parent_is_unfunded():
    pipes = [Project("A", 50, 60, must_do=True), Project("C", 30, 40, parent="B"), Project("B", 40, 30)]
    shares = {"A": 1.0, "B": 0.0, "C": 0.0}
    assert round_down_and_fill(shares, pipes, 100) == {"A", "B"}


def test_a_second_project_of_an_alternative_group_is_not_added():
    pipes = [Project("A", 50, 60, must_do=True), Project("D", 20, 28, group="G"), Project("E", 25, 34, group="G")]
    shares = {"A": 1.0, "D": 1.0, "E": 0.0}
    assert round_down_and_fill(shares, pipes, 100) == {"A", "D"}
