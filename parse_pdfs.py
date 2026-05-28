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

from utils import ANON_AUT, BASE_DIR, extract_text_from_blocks, word_is_in_text


def has_absstract(text):
    pattern = "^Abstract\n?"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return not match is None


def find_relevant_blocks(blocks):
    relevant_blocks = []
    for bl in blocks:
        if has_absstract(bl[4]):
            break
        else:
            relevant_blocks.append(bl)
    return relevant_blocks


def filter_texts(texts):
    # remove sentances
    clean_texts = []
    for text in texts:
        if not has_random_words(text):
            clean_texts.append(text)
    return clean_texts


def split_and_clean_numbered_tokens(token):
    """Split a token when it is a sequence of numbered tokens"""

    pattern_with_letter = re.compile(
        r"(?:,?\s(?:\d|[^\w\s@{}])+\s?[A-Z])|(?:^(?:\d|[^\w\s@{}])+\s?[A-Z])"
    )
    pattern_no_letter = re.compile(
        r"(?:,?\s(?:\d|[^\w\s@{}])+\s?)|(?:^(?:\d|[^\w\s@{}])+\s?)"
    )

    matches = re.findall(pattern_with_letter, token)
    if len(matches) == 0:
        return [token]
    else:
        token_split = re.split(pattern_no_letter, token)
        return [x for x in token_split if x != ""]


def text_to_tokens(text):
    tokens_split = text.split("\n")
    tokens = []
    for token in tokens_split:
        tokens.extend(split_and_clean_numbered_tokens(token))
    return tokens


def texts_to_tokens(texts, conf="neurips"):
    tokens = []
    for text in texts:
        if conf == "neurips":
            tokens.extend(text_to_tokens(text))
        elif conf == "icml":
            tokens.extend(text_to_tokens_icml(text))
            if has_correspondence(text):
                break
    return tokens


CORRESPONDENCE_REGX = re.compile(r"Cor-?\n?re-?\n?spon-?\n?den-?\n?ce")


def remove_all_after_correspondence(text):
    text_split = re.split(CORRESPONDENCE_REGX, text)
    return text_split[0]


def has_correspondence(text):
    matches = re.findall(CORRESPONDENCE_REGX, text)
    return len(matches) > 0


def text_to_tokens_icml(text):
    # take text before 'Correspondence'
    text = remove_all_after_correspondence(text)
    # split to tokens by numbers
    tokens = split_and_clean_numbered_tokens(text)
    return tokens


def filter_out_title_tokens(tokens, authors_list, sim=0.7):
    while len(tokens) > 0 and not is_authors(tokens[0], authors_list, sim):
        tokens = tokens[1:]
    return tokens


def filter_tokens(tokens):
    # remove figure and contribution tokens
    clean_tokens = []
    for token in tokens:
        if (
            not is_figure_one_token(token)
            and not is_contribution_token(token)
            and not has_random_words(token)
        ):
            if (
                not is_email_string(token)
                and not is_website_string(token)
                and token != ""
                and token != "\n"
            ):
                if has_english_letter(token):
                    clean_tokens.append(token)
    return clean_tokens


def is_figure_one_token(token):
    return "figure 1" in token.lower()


def is_contribution_token(token):
    return "author" in token.lower() or "contribution" in token.lower()


def is_domain(token):
    doman_regex = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")
    return bool(doman_regex.match(token))


def is_email(token):
    return "@" in parseaddr(token)[1]


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_authors(token, authors_list, sim=0.7):
    while len(token) > 0 and not token[-1].isalpha():
        token = token[:-1]
    for author in authors_list:
        if author in token:
            return True
        if similarity(author, token) > sim:
            return True
    return False


EMAIL_LIST_REGEX = re.compile(
    r"""
    ^\s*
    (?:                                                     # first email
        [a-zA-Z0-9._%+-]+                                  # normal username
        |
        \{?[a-zA-Z0-9._%+-]+(?:\s*,\s*[a-zA-Z0-9._%+-]+)*\}  # grouped usernames
    )
    @
    [a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    (?:                                                     # additional emails
        \s*[;,]\s*
        (?:[a-zA-Z0-9._%+-]+|\{[a-zA-Z0-9._%+-]+(?:\s*,\s*[a-zA-Z0-9._%+-]+)*\})
        @
        [a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    )*
    \s*;?\s*
    $
    """,
    re.VERBOSE,
)

EMAIL_LIST_IN_THE_STRING = re.compile(
    r"""\s*(?:[a-zA-Z0-9._%+-]+|\{[a-zA-Z0-9._%+-]+(?:\s*,\s*[a-zA-Z0-9._%+-]+)*\})@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\s*[;,]\s*(?:[a-zA-Z0-9._%+-]+|\{[a-zA-Z0-9._%+-]+(?:\s*,\s*[a-zA-Z0-9._%+-]+)*\})@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})*\s*;?\s*"""
)


def is_email_string(s: str) -> bool:
    s = s.rstrip(string.whitespace + string.punctuation)
    return bool(EMAIL_LIST_REGEX.match(s))


WEB_LINK_REGEX = re.compile(
    r"""
    ^\s*
    (?<!@)                                   # don't match emails
    \b
    (?:https?://)?                           # optional scheme
    (?:www\.)?                               # optional www
    [a-z0-9-]+(?:\.[a-z0-9-]+)+         # domain
    (?::\d+)?                                # optional port
    (?:/[^\s]*)?                             # optional path/query/fragment
    \b
    """,
    re.VERBOSE,
)


def is_website_string(s):
    return bool(WEB_LINK_REGEX.match(s))


def has_english_letter(s: str) -> bool:
    return bool(re.search(r"[A-Za-z]", s))


def has_random_words(token: str) -> bool:
    random_words = (
        "kitchen",
        "corner",
        "chairs",
        "a couch",
        "living space",
        "a white ceiling",
        "to a hallway.",
        "a dining table",
        "room with",
        "that leads to",
        "is decorated with",
        "a ceiling with",
        "A bedroom with",
        "leading to",
        "camera poses.",
        "multi-view panoramas",
        "By using",
        "generate images",
        "cross-category",
        "complex trajectories",
        "high-quality",
        "however",
    )
    for rw in random_words:
        if word_is_in_text(rw, token):
            return True
    return False


def select_affiliations(tokens, authors_list, sim=0.7, max_num_aff=60):
    # filter out authors
    tokens = [x for x in tokens if not is_authors(x, authors_list, sim)]

    # a hack to reduce the amount of trash
    if len(tokens) > max_num_aff:
        tokens = tokens[:max_num_aff]
        print(f"WARNING: too many affiliations, cuttimg down to {max_num_aff}")
    return tokens


def determine_case(tokens, tokens_ft, authors_list, sim=0.7):
    """
    Case 0: authors go first with superindices, then affiliations go one after another before
        the abstract
    Case 1: affiliation of each author follow the name of the author, often with the full address
    Case 2: authors go first with superindices, then affiliations go in the footnote
    Case -1: not able to determine
    """
    if len(tokens) < 2:
        return -1

    if (
        is_authors(tokens[0], authors_list, sim)
        and is_authors(tokens[1], authors_list, sim)
    ) or (
        len(authors_list) > 1
        and authors_list[0] in tokens[0]
        and authors_list[1] in tokens[0]
    ):
        only_affs = select_affiliations(tokens, authors_list, sim)
        if len(only_affs) == 0:
            if len(tokens_ft) > 0:
                return 2
            else:
                return -1
        else:
            return 0

    if is_authors(tokens[0], authors_list, sim) and not is_authors(
        tokens[1], authors_list, sim
    ):
        return 1

    return -1


def lstrip_non_letters(token: str) -> str:
    token = token.lstrip(string.whitespace + string.punctuation + string.digits)
    if not token[0].isalpha():
        token = token[1:]
    return token


def collect_affiliations_case_0(tokens, authors_list, sim=0.7):
    # filter out authors
    tokens = select_affiliations(tokens, authors_list, sim)

    if len(tokens) == 0:
        print("No affiliationa found!")
        return []

    # if affiliations start with numebrs / symbol
    if not tokens[0][0].isalpha():
        # rmove symbols in the beginning
        tokens = [lstrip_non_letters(x) for x in tokens]

    return tokens


def collect_affiliations_case_1(tokens, authors_list, sim=0.7):
    affiliations = []
    it = 0
    while it < len(tokens):
        if is_authors(tokens[it], authors_list, sim):
            if it + 1 < len(tokens):
                aff = tokens[it + 1]
            else:
                aff = None
            it += 2
            while it < len(tokens) and not is_authors(tokens[it], authors_list, sim):
                if (
                    not is_email_string(tokens[it])
                    and not is_domain(tokens[it])
                    and not is_code(tokens[it])
                ):
                    aff = "; ".join([aff, tokens[it]])
                it += 1
            if aff is not None:
                affiliations.append(aff)
        elif is_email_string(tokens[it]):
            it += 1
        elif is_domain(tokens[it]):
            it += 1
        elif is_code(tokens[it]):
            it += 1
        else:
            print(f"WARNING: Skipping unknown token: {tokens[it]}")
            it += 1
    affiliations = np.unique(affiliations).tolist()
    return affiliations


def collect_affiliations_case_2(footnote_tokens):
    return footnote_tokens


def is_code(token):
    return "code" in token.lower()


def get_affiliations(
    pdf_file_path,
    authors_list,
    year,
    conf="neurips",
    sim=0.7,
):
    if conf == "neurips":
        return get_affiliations_neurips(pdf_file_path, authors_list, sim)
    elif conf == "icml":
        return get_affiliations_icml(pdf_file_path, authors_list, year, sim)
    elif conf == "iclr":
        return get_affiliations_iclr(pdf_file_path, authors_list, sim)


def is_anonimous(tokens):
    for token in tokens:
        if ANON_AUT.lower() in token.lower():
            return True
    return False


def get_affiliations_iclr(pdf_file_path, authors_list, sim=0.7):
    doc = pymupdf.open(pdf_file_path)
    blocks = list(doc[0].get_textpage().extractBLOCKS())
    texts = extract_text_from_blocks(find_relevant_blocks(blocks))
    texts = filter_texts(texts)
    tokens = texts_to_tokens(texts)

    if is_anonimous(tokens):
        return [ANON_AUT]

    tokens = filter_out_title_tokens(tokens, authors_list, sim)
    tokens = filter_tokens(tokens)

    texts_ft = get_footnote_texts(doc[0])
    tokens_ft = texts_to_tokens(texts_ft)
    tokens_ft = filter_tokens(tokens_ft)

    # determine the case
    case = determine_case(tokens, tokens_ft, authors_list, sim)
    if case == 0:
        return collect_affiliations_case_0(tokens, authors_list, sim)
    elif case == 1:
        return collect_affiliations_case_1(tokens, authors_list, sim)
    elif case == 2:
        return collect_affiliations_case_2(tokens_ft)
    else:
        print(f"Cannot collect affiliations for file: {pdf_file_path}")
        return []


def get_affiliations_icml(pdf_file_path, authors_list, year, sim=0.7):
    doc = pymupdf.open(pdf_file_path)
    # import ipdb; ipdb.set_trace()

    if year > 2016:
        texts_ft = get_footnote_texts(doc[0], double_col=True)
        tokens_ft = texts_to_tokens(texts_ft, conf="icml")
        tokens_ft = filter_tokens(tokens_ft)
        tokens_ft = [tk.replace("\n", " ").replace("- ", "") for tk in tokens_ft]
        if len(tokens_ft) > 0:
            return tokens_ft
        else:
            return get_affiliations_neurips(pdf_file_path, authors_list, sim=0.7)
    else:
        doc = pymupdf.open(pdf_file_path)
        blocks = list(doc[0].get_textpage().extractBLOCKS())
        texts = extract_text_from_blocks(find_relevant_blocks(blocks))
        texts = filter_texts(texts)
        tokens = texts_to_tokens(texts)
        tokens = filter_out_title_tokens(tokens, authors_list, sim)
        tokens = filter_tokens(tokens)
        affs = select_affiliations(tokens, authors_list, sim)
        return affs


def get_affiliations_neurips(pdf_file_path, authors_list, sim=0.7):
    doc = pymupdf.open(pdf_file_path)
    blocks = list(doc[0].get_textpage().extractBLOCKS())
    texts = extract_text_from_blocks(find_relevant_blocks(blocks))
    texts = filter_texts(texts)
    tokens = texts_to_tokens(texts)
    tokens = filter_out_title_tokens(tokens, authors_list, sim)
    tokens = filter_tokens(tokens)

    texts_ft = get_footnote_texts(doc[0])
    tokens_ft = texts_to_tokens(texts_ft)
    tokens_ft = filter_tokens(tokens_ft)

    # determine the case
    case = determine_case(tokens, tokens_ft, authors_list, sim)
    if case == 0:
        return collect_affiliations_case_0(tokens, authors_list, sim)
    elif case == 1:
        return collect_affiliations_case_1(tokens, authors_list, sim)
    elif case == 2:
        return collect_affiliations_case_2(tokens_ft)
    else:
        print(f"Cannot collect affiliations for file: {pdf_file_path}")
        return []


def clean_up_affiliations(affiliations):
    affiliations = [x for x in affiliations if not is_email_string(x)]
    for it in range((len(affiliations))):
        matches = re.findall(EMAIL_LIST_IN_THE_STRING, affiliations[it])
        if len(matches) > 0:
            affiliations[it] = " ".join(
                re.split(EMAIL_LIST_IN_THE_STRING, affiliations[it])
            )
    affiliations = [
        s.strip(string.whitespace + string.punctuation) for s in affiliations
    ]
    return affiliations


def get_footnote_line(page):
    drawings = page.get_drawings()
    footnote_line = None
    for dr in drawings:
        if len(dr["items"]) == 1 and dr["items"][0][0] == "l":
            if (
                dr["rect"].y1 == dr["rect"].y0
                and dr["rect"].y1 > 400
                and dr["rect"].x0 < 100
                and (dr["rect"].x1 - dr["rect"].x0) > 40
            ):
                footnote_line = dr
                break
    return footnote_line


def select_footnote_blocks(footnote_line, blocks, double_col=False, err=0.9):
    y_threshold = footnote_line["rect"].y0
    x_threshold = 310
    result = []
    for bl in blocks:
        if bl[1] + err > y_threshold:
            if not double_col or bl[2] < x_threshold + err:
                result.append(bl)
    return result


def get_footnote_texts(page, double_col=False):
    ft_line = get_footnote_line(page)
    if ft_line is None:
        return []
    blocks = list(page.get_textpage().extractBLOCKS())
    ft_blocks = select_footnote_blocks(ft_line, blocks, double_col)
    ft_texts = extract_text_from_blocks(ft_blocks)

    result = []
    for txt in ft_texts:
        if not word_is_in_text("conference", txt):
            result.append(txt)

    return result


def main(args):
    year = args.year
    conf = args.conf

    info_path = f"{BASE_DIR}{conf}/papers_info_{year}.csv"
    papers_dir = Path(f"{BASE_DIR}{conf}/{year}/")
    info_data = pd.read_csv(info_path, index_col=0)
    info_data = info_data.fillna("")

    print(f"Processing papers for the year {year}")
    affiliations = []
    failed = 0
    if "hash" in info_data.columns and not (conf == "iclr" and year in [2013, 2014]):
        hashes = info_data.hash.values
    else:
        hashes = [url.split("/")[-1] for url in info_data.url.values]

    if "accepted_mc" in info_data.columns:
        acceptence_flags = info_data.accepted_mc.values
    else:
        acceptence_flags = [1] * len(hashes)
    for idx, (name, acflag) in enumerate(zip(hashes, acceptence_flags)):
        # skip clearly unrelevant papers, keep clearly accepted (1) and umbiguous (-1)
        if acflag == 0:
            affiliations.append("")
            continue
        pdf_path = papers_dir / (name + ".pdf")
        authors = info_data.authors[idx]
        if authors == "":
            print(
                f"Authors list is empty. Cannot collect affiliations for file: {pdf_path}"
            )
            aff = []
        else:
            authors = authors.split(", ")
            try:
                aff = get_affiliations(pdf_path, authors, year, conf)
                aff = clean_up_affiliations(aff)
            except IndexError as e:
                print(
                    f"Cannot collect affiliations for file: {pdf_path} due to the error {e}"
                )
                aff = []
        if len(aff) == 0:
            failed += 1
            print(f"Did not collect affiliations for file: {pdf_path}")

        affiliations.append("\n".join(aff))

    info_data["aff"] = affiliations

    print(f"Faled to collect affiliations: {failed}")

    output_filename = info_path[:-4] + "_aff.csv"
    info_data.to_csv(output_filename)

    print(f"Saved file at {output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--conf", type=str, default="neurips")
    args = parser.parse_args()
    main(args)
