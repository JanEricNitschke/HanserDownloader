"""Script to download all pdfs for a book from the hanser verlag

Typical usage example:
    python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://www.hanser-elibrary.com/isbn/9783446453968"
"""
#!/usr/bin/env python

import sys
import os
import logging
import argparse
import requests
from bs4 import BeautifulSoup


def main(args):
    """Downloads demos from hltv.org"""
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
        default="https://downloads.hanser.de/index.asp?isbn=978-3-446-43085-3&nav_id=763475834&nav_page=2",
        help="Url to the book to download",
    )
    options = parser.parse_args(args)

    # Creates the directory to store the pdfs in if it does not exist yet
    if not os.path.exists(options.dir):
        os.makedirs(options.dir)

    logfile = os.path.join(options.dir, "download.log")
    if options.debug:
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

    # Requests URL and get response object
    response = requests.get(url, timeout=100)

    # Parse text obtained
    soup = BeautifulSoup(response.text, "html.parser")

    # For the Hanser Verlag the Chapter titles can be found like this (26.12.2022 9:07):
    # <h5>Die Konkubinenwirtschaft</h5>
    # document.querySelector("#\\31 0\\.3139\\/9783446418240\\.fm > h5")
    # /html/body/div[1]/div/main/div[2]/div[2]/div/div[1]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/a/h5
    # Get all h5 headings that do not have a class and get their inner text:
    # Should result in a list like this:
    # ['Die Konkubinenwirtschaft', 'Nicht lange Fackeln', 'Auf und Nieder immer wieder', 'Immer flüssig', 'Wahaha', 'Stets starkes Signal', 'Mit Mann und Maus',
    # 'QQ ohne IQ', 'Akku leer', 'Bohren für China', 'Über den Wolken', 'Haier und Higher', 'Störsender und Chinesin',
    # 'Hochstapeln leicht gemacht', 'Meisterzeit', 'Literaturverzeichnis']
    # Order should be the same as that of the links
    names = list(map(lambda h5: h5.text.strip(), soup.find_all("h5", {"class": ""})))

    # Find all hyperlinks present on webpage
    # link_url = link.get("href") # /doi/epdf/10.3139/9783446456013.012
    # link_url = "https://www.hanser-elibrary.com" + link_url # https://www.hanser-elibrary.com/doi/epdf/10.3139/9783446456013.012
    # link_url = link_url.replace("epdf", "pdf") # https://www.hanser-elibrary.com/doi/pdf/10.3139/9783446456013.012
    # For the Hanser Verlag the pdf link elements look like this (26.12.2022 8:48):
    # <a title="PDF" class="btn btn--light-bg" href="/doi/epdf/10.3139/9783446456013.012"><i aria-hidden="true" class="icon-PDF inline-icon"></i><span class="text">PDF</span></a>
    # The full xpath/jspath of the elements are (26.12.2022 8:48):
    # /html/body/div[1]/div/main/div[2]/div[2]/div/div[1]/div[3]/div[2]/div[14]/div/div/div[3]/ul/li[2]/a
    # document.querySelector("#pb-page-content > div > main > div.container.shift-up-content > div.page__content.padding-wrapper.table-of-content-page > div > div.col-lg-8.col-md-8 >
    # div.toc-container > div.table-of-content > div:nth-child(1) > div > div > div.issue-item__footer > ul > li:nth-child(2) > a")
    links = list(
        map(
            lambda link: ("https://www.hanser-elibrary.com" + link.get("href")).replace(
                "epdf", "pdf"
            ),
            filter(lambda link: link.get("title") == "PDF", soup.find_all("a")),
        )
    )

    if len(names) != len(links):
        raise AssertionError(
            "Could not find an equal number of chapter names and link!"
        )
    i = 0

    # From all links check for pdf link and
    # if present download file
    for link_url in links:
        i += 1
        logging.info("Downloading file: %s", i)

        logging.info("Downloading pdf from link: %s", link_url)

        # Get response object for link
        response = requests.get(link_url, timeout=100)

        # Write content in pdf file
        filename = os.path.join(options.dir, f"Chapter{i}_{names[i-1]}.pdf")
        logging.info("Saving file to %s", filename)
        # Add try except for invalid file names
        # OSError: [Errno 22] Invalid argument: 'D:\\Downloads\\Hanser\\Chapter7_EIN GEGENMODELL IM WERDEN?.pdf'
        with open(filename, "wb") as pdf:
            pdf.write(response.content)
        logging.info("File %s downloaded", i)

    logging.info("All PDF files downloaded")


if __name__ == "__main__":
    main(sys.argv[1:])
