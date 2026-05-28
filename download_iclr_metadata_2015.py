import csv
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils import BASE_DIR

URL = "https://iclr.cc/archive/www/doku.php%3Fid=iclr2015:accepted-main.html"
OUTPUT_DIR = BASE_DIR + "iclr"
year = 2015

# Fetch page
html = requests.get(URL).text
soup = BeautifulSoup(html, "html.parser")

start_h3 = soup.body.find("h3", string="Main Conference - Poster Presentations")

relevant_items = []

for sibling in start_h3.find_next_siblings():
    if sibling.name == "div":
        relevant_items.extend(list(sibling.find_all("li")))
    # Stop when next h3 appears
    if sibling.name == "h3" and sibling.text == "Workshop Papers":
        break


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
