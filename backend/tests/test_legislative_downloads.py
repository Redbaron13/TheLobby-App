import io
import json
import zipfile
from unittest import mock

from backend.legislative_downloads import download_bill_tracking_session


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

    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
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
