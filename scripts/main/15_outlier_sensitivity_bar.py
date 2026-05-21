import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import FINAL_DIR, RESULTS_DIR
from utils import setup_plotting_style


def gap_pct(july, october, agg="mean"):
    """Long-horizon gap as % change between cohort means (or medians):
    (October / July − 1) × 100. Negative = post-cutoff cohort below pre-cutoff
    (the visual 'suppression' direction). Uses % change rather than log
    points to keep units consistent with the rest of the deck and avoid
    being mistakenly compared with the diff-in-RDD coefficient."""
    f = np.median if agg == "median" else np.mean
    j = f(july)
    o = f(october)
    return (o / j - 1) * 100, len(july), len(october)


def main():
    setup_plotting_style()
    FIGURES_DIR = RESULTS_DIR / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(FINAL_DIR / "analysis_Main_2021.csv",
                     usecols=["package", "dist_to_cutoff", "post_ai_downloads_alltime"])
    july = df[(df["dist_to_cutoff"] >= -12) & (df["dist_to_cutoff"] <= -9)].copy()
    octo = df[(df["dist_to_cutoff"] >= 1) & (df["dist_to_cutoff"] <= 4)].copy()

    rows = []

    g, nj, no = gap_pct(july["post_ai_downloads_alltime"],
                            octo["post_ai_downloads_alltime"], agg="mean")
    rows.append(("Full sample (arithmetic mean)", g, nj, no))

    j2 = july[july["package"] != "mdurl"]
    g, nj, no = gap_pct(j2["post_ai_downloads_alltime"],
                            octo["post_ai_downloads_alltime"], agg="mean")
    rows.append(("Drop mdurl only (arithmetic mean)", g, nj, no))

    p99_j = july["post_ai_downloads_alltime"].quantile(0.99)
    p99_o = octo["post_ai_downloads_alltime"].quantile(0.99)
    j3 = july[july["post_ai_downloads_alltime"] < p99_j]
    o3 = octo[octo["post_ai_downloads_alltime"] < p99_o]
    g, nj, no = gap_pct(j3["post_ai_downloads_alltime"],
                            o3["post_ai_downloads_alltime"], agg="mean")
    rows.append(("Trim top 1% per cohort (arithmetic mean)", g, nj, no))

    g, nj, no = gap_pct(july["post_ai_downloads_alltime"],
                            octo["post_ai_downloads_alltime"], agg="median")
    rows.append(("Median (typical package)", g, nj, no))

    print(f"{'Spec':38s} {'Gap (%)':>10s}  {'N_July':>7s}  {'N_Oct':>7s}")
    for label, gap, nj, no in rows:
        print(f"{label:38s} {gap:>+10.1f}  {nj:>7d}  {no:>7d}")

    labels = [r[0] for r in rows]
    gaps = [r[1] for r in rows]
    colors = ["#c0392b" if g < -1 else ("#27ae60" if g > 1 else "#7f8c8d") for g in gaps]

    fig, ax = plt.subplots(figsize=(10, 4.6))
    y = np.arange(len(labels))[::-1]
    bars = ax.barh(y, gaps, color=colors, alpha=0.85, height=0.6)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(
        "Long-horizon gap, October − July 2021 cohort\n"
        "(% difference in cumulative post-AI downloads, Nov 2022 − Jan 2026)\n"
        "Negative = post-cutoff cohort below pre-cutoff"
    )
    ax.set_title(
        "Long-Horizon Gap: Sensitivity to Outliers\n"
        "Headline gap is concentrated in a single library (mdurl); reverses under outlier-robust aggregation",
        fontweight="bold", fontsize=11)

    for bar, gap in zip(bars, gaps):
        x = bar.get_width()
        ha = "left" if x >= 0 else "right"
        offset = max(2.0, abs(x) * 0.04) * (1 if x >= 0 else -1)
        ax.text(x + offset, bar.get_y() + bar.get_height() / 2,
                f"{gap:+.0f}%", va="center", ha=ha, fontweight="bold", fontsize=10)

    xmax = max(abs(min(gaps)), abs(max(gaps))) * 1.35
    ax.set_xlim(-xmax, xmax)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    plt.tight_layout()

    out_path = FIGURES_DIR / "long_horizon_outlier_sensitivity_bar.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"\nSaved sensitivity bar to {out_path}")


if __name__ == "__main__":
    main()
