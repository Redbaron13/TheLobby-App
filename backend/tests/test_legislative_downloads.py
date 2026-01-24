import io
import json
import zipfile
from unittest import mock

import pytest

from backend import legislative_downloads
from backend.legislative_downloads import (
    LegislativeDownloadError,
    download_bill_tracking_session,
    fetch_download_path,
    list_download_entries,
    select_session_directory,
    select_text_zip,
)


class FakeResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _json_bytes(value) -> bytes:
    return json.dumps(value).encode("utf-8")


def test_download_bill_tracking_session_extracts_files(tmp_path):
    api_responses = [
        _json_bytes([{"Download_Path": "/leg-databases"}]),
        _json_bytes(
            [
                {
                    "FileName": "2024data",
                    "Type": "D",
                    "DateModified": "",
                    "Ext": "",
                    "DownloadType": "Bill_Tracking",
                }
            ]
        ),
        _json_bytes(
            [
                {
                    "FileName": "DB2024_TEXT.zip",
                    "Type": "F",
                    "DateModified": "",
                    "Ext": ".zip",
                    "DownloadType": "Bill_Tracking",
                }
            ]
        ),
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("MAINBILL.TXT", "header\n")
        archive.writestr("ROSTER.TXT", "header\n")
        archive.writestr("BILLSPON.TXT", "header\n")
        archive.writestr("COMEMBER.TXT", "header\n")
    zip_bytes = zip_buffer.getvalue()

    response_queue = [*api_responses, zip_bytes]

    def fake_urlopen(_):
        payload = response_queue.pop(0)
        return FakeResponse(payload)

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen) as urlopen_mock:
        extracted = download_bill_tracking_session(
            base_url="https://www.njleg.state.nj.us",
            pub_base_url="https://pub.njleg.state.nj.us",
            download_type="Bill_Tracking",
            session_year=2024,
            destination=tmp_path,
            required_files=(
                "MAINBILL.TXT",
                "ROSTER.TXT",
                "BILLSPON.TXT",
                "COMEMBER.TXT",
            ),
        )

    assert (tmp_path / "MAINBILL.TXT").exists()
    assert (tmp_path / "ROSTER.TXT").exists()
    assert len(extracted) == 4
    assert urlopen_mock.call_count == 4


def test_fetch_download_path_rejects_non_list() -> None:
    with mock.patch.object(
        legislative_downloads,
        "_fetch_json",
        side_effect=LegislativeDownloadError("Unexpected API response format"),
    ):
        with pytest.raises(LegislativeDownloadError, match="Unexpected API response format"):
            fetch_download_path("https://www.njleg.state.nj.us", "Bill_Tracking")


def test_fetch_download_path_rejects_empty_list() -> None:
    with mock.patch.object(legislative_downloads, "_fetch_json", return_value=[]):
        with pytest.raises(LegislativeDownloadError, match="No download path"):
            fetch_download_path("https://www.njleg.state.nj.us", "Bill_Tracking")


def test_fetch_download_path_missing_download_path() -> None:
    with mock.patch.object(legislative_downloads, "_fetch_json", return_value=[{}]):
        with pytest.raises(LegislativeDownloadError, match="Download_Path"):
            fetch_download_path("https://www.njleg.state.nj.us", "Bill_Tracking")


def test_select_session_directory_missing_year() -> None:
    entries = [
        legislative_downloads.DownloadEntry(
            name="2022data",
            entry_type="D",
            date_modified="",
            extension="",
            download_type="Bill_Tracking",
        )
    ]
    with pytest.raises(LegislativeDownloadError, match="Session directory"):
        select_session_directory(entries, 2024)


def test_select_text_zip_falls_back_to_other_zip() -> None:
    entries = [
        legislative_downloads.DownloadEntry(
            name="DB2024.zip",
            entry_type="F",
            date_modified="",
            extension=".zip",
            download_type="Bill_Tracking",
        )
    ]
    assert select_text_zip(entries, 2024) == "DB2024.zip"


def test_select_text_zip_requires_zip() -> None:
    entries = [
        legislative_downloads.DownloadEntry(
            name="Readme.txt",
            entry_type="F",
            date_modified="",
            extension=".txt",
            download_type="Bill_Tracking",
        )
    ]
    with pytest.raises(LegislativeDownloadError, match="No downloadable ZIP"):
        select_text_zip(entries, 2024)


def test_download_bill_tracking_session_missing_required_file(tmp_path) -> None:
    api_responses = [
        _json_bytes([{"Download_Path": "/leg-databases"}]),
        _json_bytes(
            [
                {
                    "FileName": "2024data",
                    "Type": "D",
                    "DateModified": "",
                    "Ext": "",
                    "DownloadType": "Bill_Tracking",
                }
            ]
        ),
        _json_bytes(
            [
                {
                    "FileName": "DB2024_TEXT.zip",
                    "Type": "F",
                    "DateModified": "",
                    "Ext": ".zip",
                    "DownloadType": "Bill_Tracking",
                }
            ]
        ),
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as archive:
        archive.writestr("MAINBILL.TXT", "header\n")
        archive.writestr("ROSTER.TXT", "header\n")
        archive.writestr("BILLSPON.TXT", "header\n")
    zip_bytes = zip_buffer.getvalue()

    response_queue = [*api_responses, zip_bytes]

    def fake_urlopen(_):
        payload = response_queue.pop(0)
        return FakeResponse(payload)

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
        with pytest.raises(LegislativeDownloadError, match="Missing required files"):
            download_bill_tracking_session(
                base_url="https://www.njleg.state.nj.us",
                pub_base_url="https://pub.njleg.state.nj.us",
                download_type="Bill_Tracking",
                session_year=2024,
                destination=tmp_path,
                required_files=(
                    "MAINBILL.TXT",
                    "ROSTER.TXT",
                    "BILLSPON.TXT",
                    "COMEMBER.TXT",
                ),
            )


def test_list_download_entries_urls() -> None:
    payload = [
        {
            "FileName": "2024data",
            "Type": "D",
            "DateModified": "",
            "Ext": "",
            "DownloadType": "Bill_Tracking",
        }
    ]
    with mock.patch.object(legislative_downloads, "_fetch_json", return_value=payload) as fetch_mock:
        list_download_entries(
            base_url="https://www.njleg.state.nj.us",
            download_path="/leg-databases",
            download_type="Bill_Tracking",
            pub_base_url="https://pub.njleg.state.nj.us",
        )

    fetch_mock.assert_called_once_with(
        "https://www.njleg.state.nj.us/api/downloads/|leg-databases/"
        "pub.njleg.state.nj.us/Bill_Tracking"
    )
