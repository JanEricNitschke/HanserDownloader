#!/usr/bin/env python
# pylint: disable=line-too-long
r"""Script to download all pdfs for a book from the hanser verlag.

Typical usage example:
    python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://www.hanser-elibrary.com/isbn/9783446453968"
"""


import argparse
import logging
import os
import re
import sys
from collections.abc import Iterable

import bs4
import requests
from bs4 import BeautifulSoup


def format_chapter_name(element: bs4.element.Tag) -> str:
    """Extracts the text from a h5 element.

    Args:
        element (bs4.element.Tag): An h5 html element

    Returns:
        str: The stripped chapter name
    """
    return element.text.strip()


def get_chapter_names_from_soup(soup: BeautifulSoup) -> list[str]:
    r"""Extracts a list of chapter names from a soup from hanser-elibrary.

    For the Hanser Verlag the Chapter titles can be found like this (26.12.2022 9:07):
    <h5>Die Konkubinenwirtschaft</h5>
    document.querySelector("#\\31 0\\.3139\\/9783446418240\\.fm > h5")
    /html/body/div[1]/div/main/div[2]/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/a/h5
    Get all h5 headings that do not have a class and get their inner text:
    Should result in a list like this:
    ['Die Konkubinenwirtschaft', 'Nicht lange Fackeln', 'Auf und Nieder immer wieder',
    'Immer flüssig', 'Wahaha', 'Stets starkes Signal', 'Mit Mann und Maus',
    'QQ ohne IQ', 'Akku leer', 'Bohren für China', 'Über den Wolken',
    'Haier und Higher', 'Störsender und Chinesin',
    'Hochstapeln leicht gemacht', 'Meisterzeit', 'Literaturverzeichnis']

    Args:
        soup (BeautifulSoup): BeautifulSoup for a hanser elibrary html page

    Returns:
        list[str]: Individual chapters of the book
    """
    # Extract all h5 elements without an explicit class
    # Take their text and put it into a list for indexing
    return list(map(format_chapter_name, soup.find_all("h5", {"class": ""})))


def format_chapter_link(element: bs4.element.Tag) -> str:
    """Extracts and formats the url from a link ('a') element.

    Args:
        element (bs4.element.Tag): An 'a' element

    Returns:
        str: The formatted chapter link.

    Raises:
        TypeError: If no fitting href value was found.
    """
    # Extract the raw link from the element
    base_link = element.get("href")  # /doi/epdf/10.3139/9783446456013.012
    if not isinstance(base_link, str):
        raise TypeError(
            "Did not find a singular href value. "
            f"Expected a string but got {base_link} of type {type(base_link)} instead!"
        )
    # Add the proper domain in front of it to get a functioning url
    full_link = (
        "https://www.hanser-elibrary.com" + base_link
    )  # https://www.hanser-elibrary.com/doi/epdf/10.3139/9783446456013.012
    # Replace the 'epdf' with 'pdf' to get the url of the raw pdf
    # without the custom viewer around it
    # https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012
    return full_link.replace("epdf", "pdf")


def get_chapter_pdf_links_from_soup(soup: BeautifulSoup) -> list[str]:
    """Extract a list of links to chapter pdfs from a soup from hanser-elibrary.

    Find all hyperlinks present on webpage
    For the Hanser Verlag the pdf link elements look like this (26.12.2022 8:48):
    <a title="PDF" class="btn btn--light-bg" href="/doi/epdf/10.3139/9783446456013.012"><i aria-hidden="true" class="icon-PDF inline-icon"></i><span class="text">PDF</span></a>
    The full xpath/jspath of the elements are (26.12.2022 8:48):
    /html/body/div[1]/div/main/div[2]/div[2]/div/div[1]/div[3]/div[2]/div[14]/div/div/div[3]/ul/li[2]/a
    document.querySelector("#pb-page-content > div > main > div.container.shift-up-content > div.page__content.padding-wrapper.table-of-content-page > div > div.col-lg-8.col-md-8 >
    div.toc-container > div.table-of-content > div:nth-child(1) > div > div > div.issue-item__footer > ul > li:nth-child(2) > a")

    Args:
        soup (BeautifulSoup): BeautifulSoup for a hanser elibrary html page

    Returns:
        list[str]: Pdf links of the individual chapters of the book.
    """
    pdf_link_elements = filter(
        lambda link: link.get("title") == "PDF", soup.find_all("a")
    )
    return list(
        map(
            format_chapter_link,
            pdf_link_elements,
        )
    )


def get_chapters(soup: BeautifulSoup) -> Iterable[tuple[int, str, str]]:
    """Create an iterable over chapter indices, names and links.

    Args:
        soup (BeautifulSoup): BeautifulSoup for a hanser elibrary html page

    Returns:
        Iterable[tuple[int, str, str]]: Iterable over (index,name,link) of chapters on the webpage
    """
    # Get the names of all the chapter
    names = get_chapter_names_from_soup(soup)
    # Get the urls for all the chapter pdfs
    links = get_chapter_pdf_links_from_soup(soup)
    # If number of names and chapter links matches return an iterable
    # over (index,name,url) for each chapter
    indices = range(1, len(links) + 1)
    if len(names) == len(links):
        return zip(indices, names, links, strict=True)
    # If there is a mismatch return an iterable over
    # (index, '', url) for each chapter
    return zip(indices, [""] * len(links), links, strict=True)


def get_filename(index: int, chapter_name: str) -> str:
    """Create a filename for each chapter based on the chapter index and name.

    Args:
        index (int): The index of the chapter
        chapter_name (str): The extracted name for the chapter
            Can be '' if no name was extracted

    Returns:
        str: The filename that the pdf of the chapter should be saved to
    """
    fill_length = 3
    if chapter_name:
        # Remove characters that windows does not allow in file names
        chapter_name = re.sub(r'[\\/*?:"<>|]', "", chapter_name)
        return f"{str(index).zfill(fill_length)}_{chapter_name}.pdf"
    return f"{str(index).zfill(fill_length)}.pdf"


def make_request(url: str) -> requests.Response:
    """Tries to make a request for the given url.

    Args:
        url (str): Url to request.

    Returns:
        requests.Response: The successful response to the request.

    Raises:
        SystemExit: If the response is not `ok`.
    """
    response = requests.get(url, timeout=100)
    if not response.ok:
        sys.exit(
            f"Request to url: '{url}' was unsuccessful "
            f"with response '{response.status_code}: {response.reason}'. Exiting!"
        )
    return response


def main(args: list[str]) -> None:
    """Downloads pdf files from hanser elibrary."""
    parser = argparse.ArgumentParser("Downloads pdf files from hanser elibrary")
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="Enable debug output."
    )
    parser.add_argument(
        "--dir",
        default="D:\\Downloads\\Hanser\\",
        help="Directory that the downloaded files should be saved to",
    )
    parser.add_argument(
        "-u",
        "--url",
        default="https://www.hanser-elibrary.com/isbn/9783446453968",
        help="Url to the book to download",
    )
    options = parser.parse_args(args)

    # Creates the directory to store the pdfs in if it does not exist yet
    if not os.path.exists(options.dir):
        os.makedirs(options.dir)

    if options.debug:
        logfile = os.path.join(options.dir, "download.log")
        logging.basicConfig(
            filename=logfile,
            encoding="utf-8",
            level=logging.DEBUG,
            filemode="w",
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        logging.basicConfig(
            encoding="utf-8",
            level=logging.INFO,
            filemode="w",
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    logging.info(
        "Running with output directory: %s and URL: %s", options.dir, options.url
    )

    # URL from which pdfs to be downloaded
    url = options.url

    # Do this instead of command line arguments so that it can be
    # bundled as a simple exe that can be clicked
    # It then opens a command line asking for the input
    # Alternatively it can also be bundled without this
    # Then it has to be actively called from the command line and
    # have the arguments entered there
    # But it still does not require a python installation then
    # url = input("Enter the url you want to download things from:") # noqa:  ERA001

    response = make_request(url)
    # Parse text obtained
    soup = BeautifulSoup(response.text, "html.parser")

    # From all links check for pdf link and
    # if present download file
    for index, name, link_url in get_chapters(soup):
        logging.info("Downloading file: %s", index)

        logging.info("Downloading pdf from link: %s", link_url)

        # Get response object for link
        response = requests.get(link_url, timeout=100)

        # Write content in pdf file
        filename = os.path.join(options.dir, get_filename(index, name))
        logging.info("Saving file to %s", filename)
        with open(filename, "wb") as pdf:
            pdf.write(response.content)
        logging.info("File %s downloaded", index)

    logging.info("All PDF files downloaded")


if __name__ == "__main__":
    main(sys.argv[1:])
