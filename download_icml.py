import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import pandas as pd
from tqdm import tqdm

from utils import BASE_DIR, download_pdf, get_soup

OUTPUT_DIR = Path(BASE_DIR) / "icml"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_papers_links(soup):
    papers = soup.find_all("div", class_="paper")
    links = []
    for pap in papers:
        links.append(
            pap.find("p", class_="links").find("a", string="Download PDF")["href"]
        )


def get_pdf_url(paper_soup):
    return paper_soup.find("p", class_="links").find("a", string="Download PDF")["href"]


def get_authors(paper_soup):
    authors = paper_soup.find("span", class_="authors").get_text()
    authors = authors.replace("\xa0", " ")
    return authors


def get_title(paper_soup):
    return paper_soup.find("p", class_="title").get_text()


def get_hash(pdf_url):
    return urlparse(pdf_url).path.split("/")[-1][:-4]


def download_a_year(year, base_url):
    soup = get_soup(base_url)
    paper_soups = soup.find_all("div", class_="paper")

    print(f"Found {len(paper_soups)} papers")

    hashes = []
    titles = []
    authors = []
    urls = []

    for ps in paper_soups:
        urls.append(get_pdf_url(ps))
        hashes.append(get_hash(urls[-1]))
        titles.append(get_title(ps))
        authors.append(get_authors(ps))

    df = pd.DataFrame(
        {"hash": hashes, "title": titles, "authors": authors, "url": urls}
    )

    info_filename = OUTPUT_DIR / f"papers_info_{year}.csv"
    df.to_csv(info_filename)
    print(f"Saved info at {info_filename}")

    papers_dir = OUTPUT_DIR / str(year)
    os.makedirs(papers_dir, exist_ok=True)

    for pdf_url, paper_hash in tqdm(zip(urls, hashes), total=len(urls)):
        filename = paper_hash + ".pdf"
        download_pdf(pdf_url, filename, papers_dir)
        time.sleep(0.5)


base_urls = {
    2025: "https://proceedings.mlr.press/v267/",
    2024: "https://proceedings.mlr.press/v235/",
    2023: "https://proceedings.mlr.press/v202/",
    2022: "https://proceedings.mlr.press/v162",
    2021: "https://proceedings.mlr.press/v139",
    2020: "https://proceedings.mlr.press/v119",
    2019: "https://proceedings.mlr.press/v97",
    2018: "https://proceedings.mlr.press/v80",
    2017: "https://proceedings.mlr.press/v70",
    2016: "https://proceedings.mlr.press/v48",
    2015: "https://proceedings.mlr.press/v37",
    2014: "https://proceedings.mlr.press/v32",
    2013: "https://proceedings.mlr.press/v28",
}

for year, base_link in base_urls.items():
    download_a_year(year, base_link)
