"""Script to download all pdfs for a book from the hanser verlag

Typical usage example:
    python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://www.hanser-elibrary.com/isbn/9783446453968"
"""
#!/usr/bin/env python

import sys
import os
import typing
import logging
import re
import argparse
import requests
import bs4
from bs4 import BeautifulSoup


def format_chapter_name(element: bs4.element.Tag) -> str:
    """Extracts the text from a h5 element

    Args:
        element (bs4.element.Tag): An h5 html element

    Returns:
        Stripped string of the text of the element"""
    return element.text.strip()


def get_chapter_names_from_soup(soup: BeautifulSoup) -> list[str]:
    """Extracts a list of chapter names from a soup from hanser-elibrary

    For the Hanser Verlag the Chapter titles can be found like this (26.12.2022 9:07):
    <h5>Die Konkubinenwirtschaft</h5>
    document.querySelector("#\\31 0\\.3139\\/9783446418240\\.fm > h5")
    /html/body/div[1]/div/main/div[2]/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/a/h5
    Get all h5 headings that do not have a class and get their inner text:
    Should result in a list like this:
    ['Die Konkubinenwirtschaft', 'Nicht lange Fackeln', 'Auf und Nieder immer wieder', 'Immer flüssig', 'Wahaha', 'Stets starkes Signal', 'Mit Mann und Maus',
    'QQ ohne IQ', 'Akku leer', 'Bohren für China', 'Über den Wolken', 'Haier und Higher', 'Störsender und Chinesin',
    'Hochstapeln leicht gemacht', 'Meisterzeit', 'Literaturverzeichnis']

    Args:
        soup (BeautifulSoup): BeautifulSoup for a hanser elibrary html page

    Returns:
        A list of strings corresponding to the individual chapters of the book
    """
    # Extract all h5 elements without an explicity class
    # Take their text and put it into a list for indexing
    return list(map(format_chapter_name, soup.find_all("h5", {"class": ""})))


def format_chapter_link(element: bs4.element.Tag) -> str:
    """Extracts and formats the url from a link ('a') element

    Args:
        element (bs4.element.Tag): An 'a' element

    Returns:
        A formatted version of the url contained in the link element"""
    # Extract the raw link from the element
    base_link = element.get("href")  # /doi/epdf/10.3139/9783446456013.012
    if not isinstance(base_link, str):
        raise TypeError(
            f"Did not find a singular href value. Expected a string but got {base_link} of type {type(base_link)} instead!"
        )
    # Add the proper domain in fron of it to get a functioning url
    full_link = (
        "https://www.hanser-elibrary.com" + base_link
    )  # https://www.hanser-elibrary.com/doi/epdf/10.3139/9783446456013.012
    # Replace the 'epdf' with 'pdf' to get the url of the raw pdf without the custom viewer around it
    direct_link = full_link.replace(
        "epdf", "pdf"
    )  # https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012
    return direct_link


def get_chapter_pdf_links_from_soup(soup: BeautifulSoup) -> list[str]:
    """Extracts a list of links to individual chapter pdfs from a soup from hanser-elibrary

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
        A list of strings corresponding to the pdf links of the individual chapters of the book"""
    pdf_link_elements = filter(
        lambda link: link.get("title") == "PDF", soup.find_all("a")
    )
    link_urls = list(
        map(
            format_chapter_link,
            pdf_link_elements,
        )
    )
    return link_urls


def get_chapters(soup: BeautifulSoup) -> typing.Iterable[tuple[int, str, str]]:
    """Create an iterable over chapter indices, names and links

    Args:
        soup (BeautifulSoup): BeautifulSoup for a hanser elibrary html page

    Returns:
        Iterable over (index,name,link) of chapters on the webpage"""
    # Get the names of all the chapter
    names = get_chapter_names_from_soup(soup)
    # Get the urls for all the chapter pdfs
    links = get_chapter_pdf_links_from_soup(soup)
    # If number of names and chapter links matches return an iterable
    # over (index,name,url) for each chapter
    indices = range(1, len(links) + 1)
    if len(names) == len(links):
        return zip(indices, names, links)
    # If there is a mismatch return an iterable over
    # (index, '', url) for each chapter
    return zip(indices, [""] * len(links), links)


def get_filename(index: int, chapter_name: str) -> str:
    """Create a filename for each chapter based on the chapter index and name

    Args:
        index (int): The index of the chapter
        chapter_name (str): The extracted name for the chapter
                            Can be '' if no name was extracted

    Returns:
        The filename that the pdf of the chapter should be saved to"""
    fill_length = 3
    if chapter_name != "":
        # Remove characters that windows does not allow in file names
        chapter_name = re.sub(r'[\\/*?:"<>|]', "", chapter_name)
        return f"{str(index).zfill(fill_length)}_{chapter_name}.pdf"
    return f"{str(index).zfill(fill_length)}.pdf"


def main(args):
    """Downloads pdf files from hanser elibrary"""
    parser = argparse.ArgumentParser("Analyze the early mid fight on inferno")
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

    # Do this instead of command line arguments so that it can be bundled as a simple exe that can be clicked
    # It then opens a command line asking for the input
    # Alternatively it can also be bundled without this
    # Then it has to be actively called from the command line and have the arguments entered there
    # But it still does not require a python installation then
    # url = input("Enter the url you want to download things from:")

    # Requests URL and get response object
    response = requests.get(url, timeout=100)

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
