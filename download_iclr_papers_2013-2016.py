import os
import time

import pandas as pd
import requests
from tqdm import tqdm

from utils import BASE_DIR, download_pdf

OUTPUT_DIR = BASE_DIR + "iclr"


def download_papers_per_year(year):
    info_filename = OUTPUT_DIR + f"/papers_info_{year}.csv"
    info_data = pd.read_csv(info_filename)

    papers_dir = OUTPUT_DIR + "/" + str(year)
    os.makedirs(papers_dir, exist_ok=True)

    falure_count = 0
    for pdf_url in tqdm(info_data.url.values, total=len(info_data.url.values)):
        filename = pdf_url.split("/")[-1] + ".pdf"
        if year in [2013, 2014]:
            pdf_url = pdf_url.replace("/abs/", "/pdf/")
        try:
            download_pdf(pdf_url, filename, papers_dir)
        except requests.exceptions.HTTPError as e:
            print(f"Cannot download {pdf_url}")
            falure_count += 1
            continue
        time.sleep(0.5)
    print(f"Failed to download {falure_count} papers")


for year in [2013, 2014, 2015, 2016]:
    download_papers_per_year(year)
