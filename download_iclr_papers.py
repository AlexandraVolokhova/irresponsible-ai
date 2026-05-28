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


def download_pdf(pdf_url, session, filename):
    r = session.get(pdf_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)


def main(year, client):
    download_dir = f"{OUTPUT_DIR}/{year}"
    os.makedirs(download_dir, exist_ok=True)

    metadata_file = f"{OUTPUT_DIR}/papers_info_{year}.csv"
    data = pd.read_csv(metadata_file, index_col=0)

    session = client.session
    failed_urls = []
    for _, item in tqdm(data.iterrows()):
        pdf_url = item["url"]
        hash_ = item["hash"]
        filename = f"{download_dir}/{hash_}.pdf"
        if not Path(filename).exists():
            download_pdf(pdf_url, session, filename)
            time.sleep(1)


parser = argparse.ArgumentParser()
parser.add_argument("--username", type=str)  # your username on OpenReview
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

for year in range(2017, 2026):
    if year < 2024:
        main(year, client)
    else:
        main(year, client_old)
