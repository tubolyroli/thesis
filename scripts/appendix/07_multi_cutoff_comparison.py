import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import FINAL_DIR, RESULTS_ROBUSTNESS, FIG_ROBUSTNESS, CUTOFFS, DONUT_WEEKS
from utils import run_local_linear_rdd


def make_figure(res_df: pd.DataFrame) -> None:
    """Bar chart of the September boundary jump across the five cohorts.

    Uses the no-donut spec (cleanest comparison across years). Each bar
    is the Diff-in-RDD coefficient on `total_downloads_52wk` at h=26.
    """
    nodonut = res_df[~res_df["Label"].str.contains("Donut")].copy()
    order = ["Placebo_2018", "Placebo_2019", "Placebo_2020", "Main_2021", "Adoption_2023"]
    nodonut = nodonut.set_index("Label").loc[order].reset_index()

    display = {
        "Placebo_2018":  "2018",
        "Placebo_2019":  "2019",
        "Placebo_2020":  "2020\n(Peak COVID)",
        "Main_2021":     "2021\n(Main)",
        "Adoption_2023": "2023\n(Adoption)",
    }
    nodonut["Cohort"] = nodonut["Label"].map(display)

    NAVY = "#03045E"
    CYAN = "#00B4D8"
    LIGHT_GREY = "#C8CFD9"
    POS_HIGHLIGHT = "#2E8B57"
    NEG_HIGHLIGHT = "#C5302F"
    MAIN = NAVY

    colors = []
    for label, p in zip(nodonut["Label"], nodonut["P-value"]):
        if label == "Main_2021":
            colors.append(MAIN)
        elif p < 0.05:
            colors.append(POS_HIGHLIGHT if nodonut.loc[nodonut["Label"] == label, "Estimate"].iloc[0] > 0 else NEG_HIGHLIGHT)
        elif p < 0.10:
            colors.append(POS_HIGHLIGHT if nodonut.loc[nodonut["Label"] == label, "Estimate"].iloc[0] > 0 else NEG_HIGHLIGHT)
        else:
            colors.append(LIGHT_GREY)

    fig, ax = plt.subplots(figsize=(9, 5.2))

    x = np.arange(len(nodonut))
    ests = nodonut["Estimate"].values
    ses = nodonut["Std.Err"].values
    ax.bar(x, ests, yerr=1.96 * ses, color=colors, capsize=5, alpha=0.92,
           edgecolor="white", linewidth=0.8, width=0.65)
    ax.axhline(0, color="black", linewidth=1, zorder=1)

    # Annotate values + significance stars above/below each bar
    for xi, est, p in zip(x, ests, nodonut["P-value"].values):
        offset = 0.08 if est >= 0 else -0.10
        sig = "*" if p < 0.05 else ("†" if p < 0.10 else "")
        label_str = f"{est:+.2f}{sig}\n(p={p:.3f})"
        va = "bottom" if est >= 0 else "top"
        ax.text(xi, est + offset, label_str, ha="center", va=va,
                fontsize=10, color=NAVY, linespacing=1.1)

    ax.set_xticks(x)
    ax.set_xticklabels(nodonut["Cohort"].values, fontsize=11)
    ax.set_ylabel("September boundary jump (log points)", fontsize=11, color=NAVY)
    ax.set_title("Multi-cutoff placebo comparison\nDiff-in-RDD on log(1 + 52-week downloads), h = 26",
                 fontsize=12, fontweight="bold", color=NAVY, loc="left")

    ymin = min(ests.min() - 0.5, -1.4)
    ymax = max(ests.max() + 0.5, 1.4)
    ax.set_ylim(ymin, ymax)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", colors=NAVY)
    ax.tick_params(axis="y", colors=NAVY)
    ax.grid(axis="y", alpha=0.25, linestyle=":")

    # Footnote: significance legend + interpretation
    ax.text(0.0, -0.18,
            "* p < 0.05    † p < 0.10    n.s. = not significant",
            transform=ax.transAxes, fontsize=9, color="#666", ha="left")
    ax.text(1.0, -0.18,
            "Source: results/robustness/multi_cutoff_comparison.csv (no-donut spec)",
            transform=ax.transAxes, fontsize=9, color="#666", ha="right")

    plt.tight_layout()
    out = FIG_ROBUSTNESS / "multi_cutoff_comparison.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\nFigure saved: {out}")


def main():
    outcome = "total_downloads_52wk"
    final_results = []

    print(f"Comparing RDD estimates across cutoffs for {outcome}...")
    for name in CUTOFFS.keys():
        df_path = FINAL_DIR / f"analysis_{name}.csv"
        if not df_path.exists():
            continue
        df = pd.read_csv(df_path)

        # Test No-Donut and Donut
        final_results.append(run_local_linear_rdd(df, outcome, h=26, donut_weeks=None, label=name, cluster_col="dist_to_cutoff"))
        final_results.append(run_local_linear_rdd(df, outcome, h=26, donut_weeks=DONUT_WEEKS, label=f"{name} (Donut)", cluster_col="dist_to_cutoff"))

    res_df = pd.DataFrame(final_results)
    print("\n=========================================")
    print("      MULTI-CUTOFF COMPARISON RESULTS    ")
    print("=========================================\n")
    print(res_df.round(4).to_string(index=False))

    RESULTS_ROBUSTNESS.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(RESULTS_ROBUSTNESS / "multi_cutoff_comparison.csv", index=False)

    make_figure(res_df)

if __name__ == "__main__":
    main()
