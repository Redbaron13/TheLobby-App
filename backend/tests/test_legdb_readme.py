import textwrap

import pytest

from backend.legdb_readme import ReadmeError, ensure_required_tables, parse_available_tables


def test_parse_available_tables() -> None:
    readme_text = textwrap.dedent(
        """
        README.TXT for Database Tables

        MainBill
        BillSpon
        COMember
        Roster

        As of July 20, 2012, the following associations may be made:
        """
    )
    tables = parse_available_tables(readme_text)
    assert "MainBill" in tables
    assert "BillSpon" in tables


def test_ensure_required_tables() -> None:
    readme_text = textwrap.dedent(
        """
        README.TXT for Database Tables

        MainBill
        BillSpon
        COMember
        Roster
        """
    )
    ensure_required_tables(readme_text, ["MainBill", "BillSpon", "COMember", "Roster"])


def test_ensure_required_tables_missing_table() -> None:
    readme_text = textwrap.dedent(
        """
        README.TXT for Database Tables

        MainBill
        BillSpon
        Roster
        """
    )
    with pytest.raises(ReadmeError, match="COMember"):
        ensure_required_tables(readme_text, ["MainBill", "BillSpon", "COMember", "Roster"])
