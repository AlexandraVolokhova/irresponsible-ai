from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from utils import BASE_DIR

base_path = Path(BASE_DIR)

neurips_path = base_path / "neurips_bt_counts.csv"
neurips_counts = pd.read_csv(neurips_path, index_col=0)

icml_path = base_path / "icml_bt_counts.csv"
icml_counts = pd.read_csv(icml_path, index_col=0)

iclr_path = base_path / "iclr_bt_counts.csv"
iclr_counts = pd.read_csv(iclr_path, index_col=0)


def get_values(df, name):
    return df[df.name == name].drop(columns=["name"]).values[0]


labels = np.arange(2013, 2026)

# -------- ICML --------
bt_icml = get_values(icml_counts, "all_bt")
total_icml = get_values(icml_counts, "total_papers")

# -------- NeurIPS --------
bt_neurips = get_values(neurips_counts, "all_bt")
total_neurips = get_values(neurips_counts, "total_papers")

# -------- ICLR --------
bt_iclr = get_values(iclr_counts, "all_bt")
total_iclr = get_values(iclr_counts, "total_papers")


# Positions
n = len(labels)
y_pos = np.arange(n)
bar_height = 0.25

# Fractions
frac_icml = bt_icml / total_icml
frac_neurips = bt_neurips / total_neurips
frac_iclr = bt_iclr / total_iclr

# ---- Okabe–Ito colors ----
blue = "#0072B2"
green = "#009E73"
orange = "#E69F00"
gray = "#D9D9D9"
# light_gray = "#EEEEEE"
# light_gray = "#E5F5F9"
light_gray = "#C7E9E3"
light_orange = "#F2E5C4"


palette = sns.color_palette("colorblind", 3)
alpha = 0.5
palette_trans = [color + (alpha,) for color in palette]

# Plot
fig, ax = plt.subplots(figsize=(11, 6))

# ---- ICML bars ----
ax.barh(
    y_pos,
    bt_icml,
    height=bar_height,
    # color=green,
    color=palette[1],
    label="ICML: big tech",
)
ax.barh(
    y_pos,
    total_icml - bt_icml,
    left=bt_icml,
    height=bar_height,
    # color=light_gray,
    color=palette_trans[1],
    label="ICML: total",
)

# ---- NeurIPS bars ----
ax.barh(
    y_pos + bar_height,
    bt_neurips,
    height=bar_height,
    # color=orange,
    color=palette[0],
    label="NeurIPS: big tech",
)
ax.barh(
    y_pos + bar_height,
    total_neurips - bt_neurips,
    left=bt_neurips,
    height=bar_height,
    # color=light_orange,
    color=palette_trans[0],
    label="NeurIPS: total",
)

# ---- ICLR bars ----
ax.barh(
    y_pos - bar_height,
    bt_iclr,
    height=bar_height,
    # color=blue,
    color=palette[2],
    label="ICLR: big tech",
)
ax.barh(
    y_pos - bar_height,
    total_iclr - bt_iclr,
    left=bt_iclr,
    height=bar_height,
    # color=gray,
    color=palette_trans[2],
    label="ICLR: total",
)

# ---- Annotations ----
offset = max(total_neurips.max(), total_icml.max(), total_iclr.max()) * 0.004
annotation_fs = 6

for i in range(n):
    ax.text(
        total_icml[i] + offset,
        y_pos[i],
        f"{frac_icml[i]:.1%}",
        va="center",
        fontsize=annotation_fs,
    )
    ax.text(
        total_neurips[i] + offset,
        y_pos[i] + bar_height,
        f"{frac_neurips[i]:.1%}",
        va="center",
        fontsize=annotation_fs,
    )
    ax.text(
        total_iclr[i] + offset,
        y_pos[i] - bar_height,
        f"{frac_iclr[i]:.1%}",
        va="center",
        fontsize=annotation_fs,
    )

print(
    f"NeurIPS BT ratio: mean {np.mean(frac_neurips):.1%}, max {np.max(frac_neurips):.1%} on {labels[np.argmax(frac_neurips)]}"
)
print(
    f"ICML BT ratio: mean {np.mean(frac_icml):.1%}, max {np.max(frac_icml):.1%} on {labels[np.argmax(frac_icml)]}"
)
print(
    f"ICLR BT ratio: mean {np.mean(frac_iclr):.1%}, max {np.max(frac_iclr):.1%} on {labels[np.argmax(frac_iclr)]}"
)

# Axes & labels
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, size=12)
ax.set_xlabel("Number of publications", size=14)
eps = 0.5
ax.set_ylim((y_pos[0] - eps, y_pos[-1] + eps))

# Clean look
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

handles, labels_ = ax.get_legend_handles_labels()
handle_map = dict(zip(labels_, handles))
ordered_labels = [
    "NeurIPS: big tech",
    "ICML: big tech",
    "ICLR: big tech",
    "NeurIPS: total",
    "ICML: total",
    "ICLR: total",
]
ordered_handles = [handle_map[l] for l in ordered_labels]

ax.legend(
    ordered_handles,
    ordered_labels,
    ncol=2,
    columnspacing=1.5,
    handletextpad=0.6,
    fontsize=14,
)

plt.tight_layout()
plt.savefig("./bt_papers.pdf", format="pdf")
plt.savefig("./bt_papers.png", format="png")
plt.show()
