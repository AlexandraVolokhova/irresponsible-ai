import argparse
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import openreview
import pandas as pd
import requests
from tqdm import tqdm

from utils import BASE_DIR, download_pdf, get_soup

BASE_URL = "https://openreview.net"
OUTPUT_DIR = BASE_DIR + "iclr"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_metadata_per_year(year, client):
    if year > 2019:
        venue_id = f"ICLR.cc/{year}/Conference"
        notes = client.get_all_notes(
            content={"venueid": venue_id}
        )  # this usually gives only accepted submittions
    elif year in [2019, 2018]:
        invitation = f"ICLR.cc/{year}/Conference/-/Blind_Submission"
        notes = client.get_all_notes(
            invitation=invitation
        )  # this gives all the submissions, including rejected
    elif year in [2017, 2014, 2013]:
        invitation = f"ICLR.cc/{year}/conference/-/submission"
        notes = client.get_all_notes(
            invitation=invitation
        )  # this gives all the submissions, including rejected
    else:
        print(f"Cannon download {year} from OpenReview")
        return

    print(f"Found {len(notes)} papers in year {year}")

    # parse it into the pandas dataframe
    hashes = []
    urls = []
    titles = []
    authors = []
    abstracts = []
    for note in notes:
        hashes.append(note.id)
        if year > 2023:
            pdf_rel = note.content["pdf"]["value"]
            urls.append(BASE_URL + pdf_rel)
            titles.append(note.content["title"]["value"])
            authors.append(", ".join(note.content["authors"]["value"]))
            abstracts.append(note.content["abstract"]["value"])
        else:
            pdf_rel = note.content["pdf"]
            if pdf_rel.startswith("http"):
                pdf_url = pdf_rel
            else:
                pdf_url = BASE_URL + pdf_rel
            urls.append(pdf_url)
            titles.append(note.content["title"])
            authors.append(", ".join(note.content["authors"]))
            abstracts.append(None)

    df = pd.DataFrame(
        {
            "hash": hashes,
            "title": titles,
            "authors": authors,
            "url": urls,
            "abstract": abstracts,
        }
    )
    filename = OUTPUT_DIR + f"/papers_info_{year}.csv"
    df.to_csv(filename)
    print(f"Saved {filename}")


parser = argparse.ArgumentParser()
parser.add_argument("--username", type=str)  # your usernam on OpenReview
parser.add_argument("--password", type=str)  # your password on OpenReview
args = parser.parse_args()


client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net",
    username=args.username,
    password=args.password,
)
client_old = openreview.Client(
    baseurl="https://api.openreview.net",
    username=args.username,
    password=args.password,
)
for year in range(2013, 2026):
    if year < 2024:
        download_metadata_per_year(year, client_old)
    else:
        download_metadata_per_year(year, client)
