from validation import folds, leaks

# Each depot's routing model, one per month: months of one depot share roads and customers.
GROUP_OF = {
    "ash-jan": "ash", "ash-feb": "ash", "ash-mar": "ash",
    "birch-jan": "birch", "birch-feb": "birch",
    "cedar-jan": "cedar",
    "dune-jan": "dune", "dune-feb": "dune",
}
NAMES = list(GROUP_OF)


def test_depots_are_dealt_to_the_folds_in_name_order():
    one_each = {"ash-jan": "ash", "birch-jan": "birch", "cedar-jan": "cedar"}
    assert folds(list(one_each), one_each, 2) == [["ash-jan", "cedar-jan"], ["birch-jan"]]


def test_a_depot_on_both_sides_of_a_split_is_a_leak():
    assert leaks(["ash-jan", "cedar-jan"], ["ash-feb", "dune-jan"], GROUP_OF) == {"ash"}
    assert leaks(["ash-jan"], ["dune-jan"], GROUP_OF) == set()


def test_no_depot_is_split_across_folds():
    found = folds(NAMES, GROUP_OF, 2)
    assert sum(len(f) for f in found) == len(NAMES)
    for i, a in enumerate(found):
        for b in found[i + 1:]:
            assert not ({GROUP_OF[n] for n in a} & {GROUP_OF[n] for n in b})


def test_every_instance_lands_in_exactly_one_fold():
    found = folds(NAMES, GROUP_OF, 3)
    assert sorted(n for f in found for n in f) == sorted(NAMES)


def test_the_folds_do_not_depend_on_the_order_names_arrive_in():
    assert folds(NAMES, GROUP_OF, 2)[0]
    assert folds(list(reversed(NAMES)), GROUP_OF, 2) == folds(NAMES, GROUP_OF, 2)


def test_more_folds_than_depots_leaves_some_empty():
    found = folds(NAMES, GROUP_OF, 5)
    assert len(found) == 5 and found[4] == [] and sum(len(f) for f in found) == len(NAMES)
