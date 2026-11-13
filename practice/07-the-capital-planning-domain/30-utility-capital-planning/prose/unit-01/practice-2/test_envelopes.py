from envelopes import Request, oversubscribed, requested_by_year

# A city water utility's capital requests, in $k. Not the lesson's portfolio.
YEARS = [2027, 2028, 2029]


def test_single_year_requests_are_totalled():
    reqs = [Request("M1", "mains", 2027, (400,)), Request("M2", "mains", 2027, (150,)),
            Request("T1", "treatment", 2029, (900,))]
    assert requested_by_year(reqs, ["mains", "treatment"], YEARS) == {
        "mains": {2027: 550, 2028: 0, 2029: 0}, "treatment": {2027: 0, 2028: 0, 2029: 900}}


def test_oversubscribed_lists_the_excess():
    reqs = [Request("M1", "mains", 2027, (400,)), Request("M2", "mains", 2027, (150,)),
            Request("T1", "treatment", 2029, (900,)), Request("T2", "treatment", 2028, (100,))]
    envelopes = {("mains", 2027): 500, ("mains", 2028): 300, ("treatment", 2028): 400, ("treatment", 2029): 700}
    assert oversubscribed(reqs, envelopes) == [("mains", 2027, 550, 50), ("treatment", 2029, 900, 200)]


def test_a_multi_year_request_counts_in_each_year():
    reqs = [Request("T1", "treatment", 2027, (500, 300, 100)), Request("M1", "mains", 2028, (200,))]
    assert requested_by_year(reqs, ["mains", "treatment"], YEARS) == {
        "mains": {2027: 0, 2028: 200, 2029: 0}, "treatment": {2027: 500, 2028: 300, 2029: 100}}
    envelopes = {("treatment", 2027): 600, ("treatment", 2028): 250}
    assert oversubscribed(reqs, envelopes) == [("treatment", 2028, 300, 50)]


def test_a_request_at_its_envelope_is_not_over():
    reqs = [Request("M1", "mains", 2027, (500,)), Request("T1", "treatment", 2027, (800,))]
    envelopes = {("mains", 2027): 500, ("treatment", 2027): 700}
    assert oversubscribed(reqs, envelopes) == [("treatment", 2027, 800, 100)]


def test_a_program_with_no_requests_still_has_every_year():
    reqs = [Request("M1", "mains", 2028, (250,))]
    assert requested_by_year(reqs, ["mains", "meters", "treatment"], YEARS) == {
        "mains": {2027: 0, 2028: 250, 2029: 0}, "meters": {2027: 0, 2028: 0, 2029: 0},
        "treatment": {2027: 0, 2028: 0, 2029: 0}}
