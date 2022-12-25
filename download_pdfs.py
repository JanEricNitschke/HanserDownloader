"""Script to download all pdfs for a book from the hanser verlag

Typical usage example:
    python download_pdfs.py --dir "D:\\Downloads\\Hanser\\" --url "https://downloads.hanser.de/index.asp?isbn=978-3-446-43085-3&nav_id=763475834&nav_page=2"
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

    # URL from which pdfs to be downloaded
    url = options.url

    # Requests URL and get response object
    response = requests.get(url)

    # Parse text obtained
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all hyperlinks present on webpage
    links = soup.find_all("a")

    i = 0

    # From all links check for pdf link and
    # if present download file
    for link in links:
        if any(
            pdf_identifier in link.get("href", [])
            for pdf_identifier in [".pdf", "/pdf"]
        ):
            i += 1
            logging.info("Downloading file: %s", i)

            # Get response object for link
            response = requests.get(link.get("href"))

            # Write content in pdf file
            filename = os.path.join(options.dir, "pdf" + str(i) + ".pdf")
            logging.info("Saving file to %s", filename)
            with open(filename, "wb") as pdf:
                pdf.write(response.content)
            logging.info("File %s downloaded", i)

    logging.info("All PDF files downloaded")


if __name__ == "__main__":
    main(sys.argv[1:])
