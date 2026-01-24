from backend.data_merge import merge_rows_by_key


def test_merge_rows_by_key_keeps_latest_date() -> None:
    rows = [
        {"bill_key": "A-1", "mod_date": "2023-01-01", "value": "older"},
        {"bill_key": "A-1", "mod_date": "2024-01-01", "value": "newer"},
        {"bill_key": "B-2", "mod_date": "2022-05-01", "value": "keep"},
    ]
    merged = merge_rows_by_key(rows, "bill_key", ["mod_date"])
    merged_map = {row["bill_key"]: row for row in merged}
    assert merged_map["A-1"]["value"] == "newer"
    assert merged_map["B-2"]["value"] == "keep"
