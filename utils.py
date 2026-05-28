import os
import re
import time
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PDFDownloader/1.0)"}
ANON_AUT = "Anonymous authors"
BASE_DIR = "./papers/"


def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def get_paper_links(list_page, base_url=BASE_URL):
    """Return list of paper detail page URLs."""
    soup = get_soup(list_page)
    year = list_page.split("/")[-1]
    links = []
    # Find anchors pointing to each paper’s detail page
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if f"/paper_files/paper/{year}/" in href:
            full_url = urljoin(base_url, href)
            links.append(full_url)
    # dedupe
    return list(dict.fromkeys(links))


def get_paper_hash(abs_url):
    parsed = urlparse(abs_url)
    return parsed.path.split("/")[5].split("-")[0]


def get_track(soup):
    elem = soup.find("span", class_="paper-track")
    if elem is not None:
        return elem.text
    else:
        return ""


def download_pdf(pdf_url, filename, download_dir):
    """Download the PDF to disk."""
    local_path = os.path.join(download_dir, filename)
    if os.path.exists(local_path):
        print(f"Exists: {filename}")
        return
    r = requests.get(pdf_url, headers=HEADERS, stream=True)
    r.raise_for_status()
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)


def word_is_in_text(word, text):
    pattern = rf"\b{re.escape(word)}\b"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return len(matches) > 0


def extract_text_from_blocks(blocks):
    return [x[4] for x in blocks]
