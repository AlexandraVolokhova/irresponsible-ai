import argparse
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import BASE_DIR, download_pdf, get_paper_hash, get_paper_links, get_soup


def extract_pdf_url(soup, root="https://papers.nips.cc"):
    div = soup.find("div", class_="paper-actions")
    for elem in div.find_all("a"):
        if elem.get_text() == "Paper":
            href = elem.get("href")
            return root + href
    raise Exception("Cannot find pdf url")


def main(args):
    year = args.year
    download_dir = Path(BASE_DIR) / f"neurips/{year}"
    os.makedirs(download_dir, exist_ok=True)

    list_page = f"https://papers.nips.cc/paper_files/paper/{year}"

    print("Fetching paper list page...")
    paper_pages = get_paper_links(list_page)
    print(f"Found {len(paper_pages)} papers")

    failed_urls = []
    for abs_url in tqdm(paper_pages):
        try:
            soup = get_soup(abs_url)
            pdf_url = extract_pdf_url(soup)
            paper_hash = get_paper_hash(abs_url)
            filename = paper_hash + ".pdf"
            try:
                download_pdf(pdf_url, filename, download_dir)
            except Exception as e:
                print("Got first exception while downlowding")
                time.sleep(5)
                try:
                    download_pdf(pdf_url, filename, download_dir)
                except Exception as e:
                    print("Got second exception while downlowding")
                    time.sleep(10)
                    download_pdf(pdf_url, filename, download_dir)
        except Exception as e:
            print(f"Failed to download {abs_url}: {e}")
            failed_urls.append(abs_url)
            continue
        time.sleep(0.5)  # be polite

    print("Done.")
    if len(failed_urls) > 0:
        print("Failed to download:")
        print(*failed_urls, sep="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year")
    args = parser.parse_args()
    main(args)
