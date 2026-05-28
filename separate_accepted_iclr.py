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

from utils import ANON_AUT, BASE_DIR, extract_text_from_blocks, word_is_in_text


def has_acceptance_signs_main_conf(texts):
    """
    Check if key collocations are present in the text which would
    indicate that the submission WAS accepted as the main conference paper.
    """
    for text in texts:
        if "Published as a conference paper" in text:
            return True
    return False


def has_nonacceptance_signs_main_conf(texts):
    """
    Check if key collocations are present in the text which would
    indicate that the submission WAS NOT accepted as the main conference paper.
    """
    for text in texts:
        if (
            "Under review as a conference paper" in text
            or "Anonymous author" in text
            or "Workshop track" in text
            or "Published as a workshop paper" in text
        ):
            return True
    return False


def main(year):
    conf = "iclr"

    info_path = f"{BASE_DIR}{conf}/papers_info_{year}.csv"
    papers_dir = Path(f"{BASE_DIR}{conf}/{year}/")
    info_data = pd.read_csv(info_path, index_col=0)
    info_data = info_data.fillna("")

    print(f"Processing papers for the year {year}")
    acceptance_flags = []
    unclear_count = 0
    if "hash" in info_data.columns:
        hashes = info_data.hash.values
    else:
        hashes = [url.split("/")[-1] for url in info_data.url.values]
    for idx, name in enumerate(hashes):
        pdf_path = papers_dir / (name + ".pdf")
        doc = pymupdf.open(pdf_path)
        try:
            blocks = list(doc[0].get_textpage().extractBLOCKS())
        except IndexError:
            acceptance_flags.append(-1)
            unclear_count += 1
            print(f"Empty document: cannot process descision for {pdf_path}")
            continue

        texts = extract_text_from_blocks(blocks)
        is_accepted = has_acceptance_signs_main_conf(texts)
        is_not_accepted = has_nonacceptance_signs_main_conf(texts)
        if is_accepted and not is_not_accepted:
            # was accepted to the main conf
            acceptance_flags.append(1)
        elif is_not_accepted and not is_accepted:
            # was not accepted to the main conf
            acceptance_flags.append(0)
        else:
            # not clear
            acceptance_flags.append(-1)
            unclear_count += 1
            print(f"Cannot determine descision for {pdf_path}")

    print(f"ICLR {year}: unclear descision for {unclear_count} papers")

    info_data["accepted_mc"] = acceptance_flags
    filename = info_path
    info_data.to_csv(filename)
    print(f"Saved {filename}")


for year in range(2015, 2026):  # years 2013-2014 needs to be processed differently
    main(year)
