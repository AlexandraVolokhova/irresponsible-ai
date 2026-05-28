import argparse
import os
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from utils import BASE_DIR, get_paper_hash, get_paper_links, get_soup, get_track

OUTPUT_DIR = Path(BASE_DIR) / "neurips"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_title(soup):
    return soup.find("h1", class_="paper-title").text


def get_authors(soup):
    return soup.find("p", class_="paper-authors").text


def main(args):
    year = args.year
    print("Fetching paper list page...")
    list_page = f"https://papers.nips.cc/paper_files/paper/{year}"
    paper_pages = get_paper_links(list_page)
    print(f"Found {len(paper_pages)} papers")

    hashes = []
    titles = []
    authors = []
    tracks = []

    for abs_url in tqdm(paper_pages):
        try:
            soup = get_soup(abs_url)
        except Exception as e:
            try:
                print("Got first exception")
                time.sleep(10.0)
                soup = get_soup(abs_url)
            except Exception as e1:
                try:
                    print("Got second exception")
                    time.sleep(20.0)
                    soup = get_soup(abs_url)
                except:
                    print("Got third exception")
                    time.sleep(30.0)
                    soup = get_soup(abs_url)
        hashes.append(get_paper_hash(abs_url))
        titles.append(get_title(soup))
        tracks.append(get_track(soup))
        authors.append(get_authors(soup))
        time.sleep(2.0)  # be polite

    df = pd.DataFrame(
        {
            "hash": hashes,
            "title": titles,
            "authors": authors,
            "track": tracks,
            "url": paper_pages,
        }
    )
    df.to_csv(OUTPUT_DIR / f"papers_info_{year}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year")
    args = parser.parse_args()
    main(args)
