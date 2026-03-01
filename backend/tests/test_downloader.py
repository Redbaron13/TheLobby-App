import urllib.request
from pathlib import Path
from unittest import mock
from backend.downloader import download_file, download_files, resolve_download_url


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@mock.patch("urllib.request.urlopen")
def test_download_file(mock_urlopen, tmp_path):
    mock_urlopen.return_value = FakeResponse(b"file content")

    url = "http://example.com/test.txt"
    destination = tmp_path

    result_path = download_file(url, destination)

    assert result_path == destination / "test.txt"
    assert result_path.exists()
    assert result_path.read_bytes() == b"file content"
    mock_urlopen.assert_called_once_with(url)


@mock.patch("backend.downloader.fetch_index_html")
@mock.patch("urllib.request.urlopen")
def test_download_files(mock_urlopen, mock_fetch_index, tmp_path):
    mock_fetch_index.return_value = '<html><a href="file1.txt">file1.txt</a></html>'
    mock_urlopen.return_value = FakeResponse(b"content")

    base_url = "http://example.com"
    filenames = ["file1.txt"]
    destination = tmp_path

    results = download_files(base_url, filenames, destination)

    assert len(results) == 1
    assert results[0] == destination / "file1.txt"
    assert results[0].exists()
    assert results[0].read_bytes() == b"content"


def test_resolve_download_url():
    index_html = '<html><a href="subdir/file.txt">link</a></html>'
    base_url = "http://example.com"

    url = resolve_download_url(base_url, index_html, "file.txt")
    assert url == "http://example.com/subdir/file.txt"

    url = resolve_download_url(base_url, index_html, "other.txt")
    assert url == "http://example.com/other.txt"
