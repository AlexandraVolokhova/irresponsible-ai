import csv
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils import BASE_DIR

URL = "https://iclr.cc/archive/www/doku.php%3Fid=iclr2016:accepted-main.html"
OUTPUT_DIR = BASE_DIR + "iclr"
year = 2016

# Fetch page
html = requests.get(URL).text
soup = BeautifulSoup(html, "html.parser")


relevant_items = list(soup.body.find_all("li"))[1:]


def parse_item(item):
    title = item.a.text
    authors = item.div.contents[-1].lstrip(", ").strip()
    authors = authors.replace(" and ", ", ").replace(",,", ",")
    href = item.div.a["href"]
    pdf_link = href.replace("/abs/", "/pdf/")
    return title, authors, pdf_link


papers = []

for item in relevant_items:
    title, authors, link = parse_item(item)
    papers.append(
        {
            "title": title,
            "authors": authors,
            "url": link,
        }
    )

df = pd.DataFrame(papers)

filename = OUTPUT_DIR + f"/papers_info_{year}.csv"
df.to_csv(filename)
print(f"Saved {filename}")
