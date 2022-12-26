from unittest.mock import patch
from download_pdfs import (
    get_chapter_names_from_soup,
    format_chapter_name,
    format_chapter_link,
    get_chapter_pdf_links_from_soup,
    get_chapters,
    get_filename,
)
from bs4 import BeautifulSoup


class TestHanserDownload:
    """Class to test download_pdfs.py"""

    def setup_class(self):
        """Setup class getting a TicTacToe object"""
        with open(
            "tests/Big Data in der Praxis.html", "r", encoding="utf-8"
        ) as soup_file:
            self.soup = BeautifulSoup(soup_file, "html.parser")

    def teardown_class(self):
        """Set tictactoe to None"""
        self.soup = None

    def test_format_chapter_name(self):
        """Tests format_chapter_name"""
        tag = BeautifulSoup("<h5>Big Data in der Praxis</h5>", "html.parser").h5
        expected_result = "Big Data in der Praxis"
        result = format_chapter_name(tag)
        assert isinstance(result, str)
        assert result == expected_result

    def test_get_chapter_names_from_soup(self):
        """Tests get_chapter_names_from_soup"""
        expected_list = [
            "Big Data in der Praxis",
            "Einleitung",
            "Big Data",
            "Hadoop",
            "Das Hadoop-Ecosystem",
            "NoSQL und HBase",
            "Data Warehousing mit Hive",
            "Big-Data-Visualisierung",
            "Auf dem Weg zu neuem Wissen – Aufbereiten, Anreichern und Empfehlen",
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
        """Tests format_chapter_link"""
        tag = BeautifulSoup(
            '<a title="PDF" class="btn btn--light-bg" href="/doi/epdf/10.3139/9783446456013.012"><i aria-hidden="true" class="icon-PDF inline-icon"></i><span class="text">PDF</span></a>',
            "html.parser",
        ).a
        expected_result = (
            "https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012"
        )
        result = format_chapter_link(tag)
        assert isinstance(result, str)
        assert result == expected_result

    def test_get_chapter_pdf_links_from_soup(self):
        """Tests get_chapter_pdf_links_from_soup"""
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
    def test_get_chapter(self, link_mock, name_mock):
        """Tests get_chapter"""
        link_mock.side_effect = [["/1", "/2", "/3"], ["/1", "/2", "/3"]]
        name_mock.side_effect = [["a", "b", "c"], ["/1", "/2"]]
        result1 = get_chapters(self.soup)
        assert isinstance(result1, zip)
        assert list(result1) == [(1, "a", "/1"), (2, "b", "/2"), (3, "c", "/3")]
        result2 = get_chapters(self.soup)
        assert isinstance(result2, zip)
        assert list(result2) == [(1, "", "/1"), (2, "", "/2"), (3, "", "/3")]

    def test_get_filename(self):
        """Tests get_filename"""
        result = get_filename(3, "test")
        assert isinstance(result, str)
        assert result == "Chapter3_test.pdf"
        result = get_filename(23, "Was tun?")
        assert isinstance(result, str)
        assert result == "Chapter23_Was tun.pdf"
