from datetime import date

from backend.session_filter import build_session_window, filter_rows_by_date


def test_build_session_window_uses_lookback() -> None:
    window = build_session_window(lookback_sessions=3, session_length_years=2, today=date(2025, 5, 1))
    assert window.cutoff_date == date(2019, 1, 1)


def test_filter_rows_by_date_respects_cutoff() -> None:
    cutoff = date(2023, 1, 1)
    rows = [
        {"mod_date": "2024-01-02"},
        {"mod_date": "2022-12-31"},
        {"mod_date": None},
    ]
    filtered = filter_rows_by_date(rows, ["mod_date"], cutoff)
    assert filtered == [rows[0], rows[2]]
