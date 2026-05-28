import argparse
import itertools
import re
import string
from difflib import SequenceMatcher
from email.utils import parseaddr
from pathlib import Path

import ipdb
import numpy as np
import pandas as pd
import pymupdf
import spacy

from utils import BASE_DIR


def main(year):
    conf = "iclr"

    info_path = f"{BASE_DIR}{conf}/papers_info_{year}.csv"
    papers_dir = Path(f"{BASE_DIR}{conf}/{year}/")
    info_data = pd.read_csv(info_path, index_col=0)
    info_data = info_data.fillna("")

    titles_file = f"./titles_iclr_{year}.txt"

    with open(titles_file, "r") as file:
        accepted_titles = file.readlines()
    clip = 60
    accepted_titles_clipped = [x.strip().lower()[:clip] for x in accepted_titles]

    print(f"Processing papers for the year {year}")

    acceptance_flags = []

    for title in info_data.title.values:
        title = title.strip().lower()
        acceptance_flags.append(int(title[:clip] in accepted_titles_clipped))

    print(
        f"Matched accepted: {sum(acceptance_flags)}, reference accepted {len(accepted_titles)}"
    )

    info_data["accepted_mc"] = acceptance_flags
    filename = info_path
    info_data.to_csv(filename)
    print(f"Saved {filename}")


for year in range(2013, 2015):
    main(year)
