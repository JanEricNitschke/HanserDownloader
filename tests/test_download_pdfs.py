"""Tests download_pdfs.py."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from bs4 import BeautifulSoup

from download_pdfs import (
    format_chapter_link,
    format_chapter_name,
    get_chapter_names_from_soup,
    get_chapter_pdf_links_from_soup,
    get_chapters,
    get_filename,
    make_request,
)


class TestHanserDownload:
    """Class to test download_pdfs.py."""

    def setup_class(self):
        """Setup class getting a bs4 for the test html file."""
        with open("tests/Big Data in der Praxis.html", encoding="utf-8") as soup_file:
            self.soup = BeautifulSoup(soup_file, "html.parser")

    def teardown_class(self):
        """Set bs4 to None."""
        self.soup = None

    def test_format_chapter_name(self):
        """Tests format_chapter_name."""
        tag = BeautifulSoup("<h5>Big Data in der Praxis</h5>", "html.parser").h5
        expected_result = "Big Data in der Praxis"
        result = format_chapter_name(tag)
        assert isinstance(result, str)
        assert result == expected_result

    def test_get_chapter_names_from_soup(self):
        """Tests get_chapter_names_from_soup."""
        expected_list = [
            "Big Data in der Praxis",
            "Einleitung",
            "Big Data",
            "Hadoop",
            "Das Hadoop-Ecosystem",
            "NoSQL und HBase",
            "Data Warehousing mit Hive",
            "Big-Data-Visualisierung",
            "Auf dem Weg zu neuem Wissen – Aufbereiten, Anreichern und Empfehlen",  # noqa: RUF001, E501
            "Infrastruktur",
            "Programmiersprachen",
            "Polyglot Persistence",
            "Apache Kafka",
            "Data Processing Engines",
            "Streaming",
            "Data Governance",
            "Zusammenfassung und Ausblick",
            "Häufige Fehler",
            "Anleitungen",
            "Literaturverzeichnis",
            "Index",
        ]
        result = get_chapter_names_from_soup(self.soup)
        assert isinstance(result, list)
        assert isinstance(result[0], str)
        assert len(result) == 21
        assert result == expected_list

    def test_format_chapter_link(self):
        """Tests format_chapter_link."""
        tag = BeautifulSoup(
            '<a title="PDF" class="btn btn--light-bg" '
            'href="/doi/epdf/10.3139/9783446456013.012">'
            '<i aria-hidden="true" class="icon-PDF '
            'inline-icon"></i><span class="text">PDF</span></a>',
            "html.parser",
        ).a
        expected_result = (
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012"
        )
        result = format_chapter_link(tag)
        assert isinstance(result, str)
        assert result == expected_result

    def test_get_chapter_pdf_links_from_soup(self):
        """Tests get_chapter_pdf_links_from_soup."""
        expected_list = [
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.fm",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.001",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.002",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.003",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.004",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.005",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.006",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.007",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.008",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.009",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.010",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.011",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.013",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.014",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.015",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.016",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.017",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.018",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.019",
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.bm",
        ]
        result = get_chapter_pdf_links_from_soup(self.soup)
        assert isinstance(result, list)
        assert isinstance(result[0], str)
        assert len(result) == 21
        assert result == expected_list

    @patch("download_pdfs.get_chapter_names_from_soup")
    @patch("download_pdfs.get_chapter_pdf_links_from_soup")
    def test_get_chapter(self, link_mock: MagicMock, name_mock: MagicMock):
        """Tests get_chapter."""
        link_mock.side_effect = [["/1", "/2", "/3"], ["/1", "/2", "/3"]]
        name_mock.side_effect = [["a", "b", "c"], ["/1", "/2"]]
        result1 = get_chapters(self.soup)
        assert isinstance(result1, zip)
        assert list(result1) == [(1, "a", "/1"), (2, "b", "/2"), (3, "c", "/3")]
        result2 = get_chapters(self.soup)
        assert isinstance(result2, zip)
        assert list(result2) == [(1, "", "/1"), (2, "", "/2"), (3, "", "/3")]

    def test_get_filename(self):
        """Tests get_filename."""
        result = get_filename(3, "test")
        assert isinstance(result, str)
        assert result == "003_test.pdf"
        result = get_filename(23, "Was tun?")
        assert isinstance(result, str)
        assert result == "023_Was tun.pdf"
        result = get_filename(12, "")
        assert isinstance(result, str)
        assert result == "012.pdf"

    @patch("download_pdfs.requests.get")
    def test_bad_response(self, get_mock: MagicMock):
        """Tests treatment of bad response."""
        dummy_status_code = 999
        dummy_reason = "Test failed successfully!"
        type(get_mock.return_value).ok = PropertyMock(return_value=False)
        type(get_mock.return_value).status_code = PropertyMock(
            return_value=dummy_status_code
        )
        type(get_mock.return_value).reason = PropertyMock(return_value=dummy_reason)
        dummy_url = "dummy_url"
        with pytest.raises(
            SystemExit,
            match=f".*{dummy_url}.*{dummy_status_code}.*{dummy_reason}.*Exiting!",
        ):
            make_request(dummy_url)

    @patch("download_pdfs.requests.get")
    def test_good_response(self, get_mock: MagicMock):
        """Tests treatment of good response."""
        dummy_url = "dummy_url"
        dummy_status_code = 200
        type(get_mock.return_value).ok = PropertyMock(return_value=True)
        type(get_mock.return_value).status_code = PropertyMock(
            return_value=dummy_status_code
        )
        test_response = make_request(dummy_url)
        assert test_response.status_code == dummy_status_code
        assert test_response.ok is True
