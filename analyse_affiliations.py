import argparse
import itertools
import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

from utils import ANON_AUT, BASE_DIR


def get_affiliations_with_substr(substr, data):
    pattern = rf"\b{re.escape(substr)}\b"
    affs = []
    indecies = []
    for idx, row in data.iterrows():
        matches = re.findall(pattern, row.aff, flags=re.IGNORECASE)
        # matches = re.findall(pattern, row.aff)
        if len(matches) > 0:
            affs.append(row.aff)
            indecies.append(idx)
    return np.array(affs), np.array(indecies)


companies_list = [
    "Alibaba",
    "Amazon",
    "AWS",
    "Apple",
    "Element AI",
    "ServiceNow",
    "Facebook",
    "Meta",
    "Google",
    "DeepMind",
    "Huawei",
    "IBM",
    "Intel",
    "Microsoft",
    "Nvidia",
    "OpenAI",
    "Samsung",
    "Baidu",
    "Salesforce",
    "Tesla",
    "Uber",
    "Anthropic",
    "xAI",
]


def main(args):
    conf = args.conf

    affs_per_year = dict()
    counts_per_year = dict()

    all_years = np.arange(2013, 2026)
    years = []

    for year in all_years:
        data_path = f"{BASE_DIR}{conf}/papers_info_{year}_aff.csv"
        if not Path(data_path).exists():
            continue
        years.append(year)
        data = pd.read_csv(data_path, index_col=0)
        data["aff"] = data["aff"].fillna("")

        # remove rejected papers (with anonymous authors)
        data = data[data.aff != ANON_AUT]
        if "accepted_mc" in data.columns:
            data = data[data.accepted_mc != 0]

        affs_year = []
        index_year = []
        for comp in companies_list:
            affs, index = get_affiliations_with_substr(comp, data)

            affs_year.append(affs)
            index_year.append(index)

        aff_all_bt = np.concatenate(affs_year, axis=0)
        index_all_bt = np.concatenate(index_year, axis=0)
        index_unique_bt, index_index_bt = np.unique(index_all_bt, return_index=True)

        # add all BT
        index_year.append(index_unique_bt)
        affs_year.append(aff_all_bt[index_index_bt])

        # add all
        index_year.append(np.arange(len(data)))
        affs_year.append(data["aff"].values)

        print(
            f"{year} BT papers: {len(index_unique_bt)}/{len(data)}, {len(index_unique_bt)/len(data)}"
        )

        affs_per_year[year] = {
            "index": [x.tolist() for x in index_year],
            "affs": [x.tolist() for x in affs_year],
        }
        counts_per_year[year] = [len(x) for x in index_year]

    df_affs = {"name": companies_list + ["all_bt", "total_papers"]}
    for year in years:
        df_affs[f"{year}_aff"] = affs_per_year[year]["affs"]
        df_affs[f"{year}_index"] = affs_per_year[year]["index"]

    df_affs = pd.DataFrame(df_affs)

    df_counts = {"name": df_affs.name.values}
    df_counts.update(counts_per_year)
    df_counts = pd.DataFrame(df_counts)

    output_root = Path(BASE_DIR)
    output_path_affs = output_root / f"{conf}_bt_affs.csv"
    output_path_counts = output_root / f"{conf}_bt_counts.csv"

    df_affs.to_csv(output_path_affs)
    print(f"Saved file to {output_path_affs}")
    df_counts.to_csv(output_path_counts)
    print(f"Saved file to {output_path_counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", type=str, default="neurips")
    args = parser.parse_args()
    main(args)
