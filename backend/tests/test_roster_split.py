from backend.roster_split import split_legislators


def test_split_legislators_separates_former() -> None:
    legislators = [
        {"roster_key": 1, "leg_status": "Active"},
        {"roster_key": 2, "leg_status": "Former"},
        {"roster_key": 3, "leg_status": "Resigned"},
        {"roster_key": 4, "leg_status": None},
    ]
    active, former = split_legislators(legislators)
    assert [leg["roster_key"] for leg in active] == [1, 4]
    assert [leg["roster_key"] for leg in former] == [2, 3]
