import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import RAW_DIR, FINAL_DIR, FIG_MAIN, CHATGPT_RELEASE, GPT4_RELEASE, MAIN_CUTOFF_NAME, DONUT_WEEKS, CUTOFFS
from utils import setup_plotting_style, normalize_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trim-top-pct", type=float, default=None,
                        help="Drop top N%% of packages per cohort by post_ai_downloads_alltime before aggregating. "
                             "Default None = full sample (original behaviour).")
    parser.add_argument("--side-by-side", action="store_true",
                        help="Produce a 1x2 figure: median (left) vs mean (right). "
                             "When set, --trim-top-pct is ignored.")
    args = parser.parse_args()
    trim_top_pct = args.trim_top_pct

    setup_plotting_style()
    FIG_MAIN.mkdir(parents=True, exist_ok=True)

    print("Loading datasets for trajectory visualization...")
    # 1. Load the cross-sectional analysis file for cohort assignment
    df_meta = pd.read_csv(FINAL_DIR / "analysis_Main_2021.csv",
                          usecols=["package", "dist_to_cutoff", "release_week", "post_ai_downloads_alltime"])
    
    # Define July vs October cohorts based on dist_to_cutoff
    # Donut is -8 to 0 (Aug/Sept). 
    # July: -12 to -9
    # October: 1 to 4
    df_meta["cohort"] = "Other"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= -12) & (df_meta["dist_to_cutoff"] <= -9), "cohort"] = "July 2021 (Pre-Cutoff)"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= 1) & (df_meta["dist_to_cutoff"] <= 4), "cohort"] = "October 2021 (Post-Cutoff)"
    
    df_meta = df_meta[df_meta["cohort"] != "Other"].copy()
    print(f"  Cohort sizes before trim: {df_meta['cohort'].value_counts().to_dict()}")

    # Optional: drop top N% per cohort by post_ai_downloads_alltime
    if trim_top_pct is not None:
        for cohort_name in df_meta["cohort"].unique():
            mask = df_meta["cohort"] == cohort_name
            threshold = df_meta.loc[mask, "post_ai_downloads_alltime"].quantile(1 - trim_top_pct / 100)
            drop_mask = mask & (df_meta["post_ai_downloads_alltime"] > threshold)
            dropped = df_meta.loc[drop_mask].nlargest(3, "post_ai_downloads_alltime")[["package", "post_ai_downloads_alltime"]]
            print(f"  [{cohort_name}] top {trim_top_pct}% trim: dropping {drop_mask.sum()} packages (p{100 - trim_top_pct:.0f} threshold={threshold:,.0f})")
            print(f"    Top 3 dropped: {dropped.to_dict('records')}")
            df_meta = df_meta[~drop_mask]
        print(f"  Cohort sizes after trim: {df_meta['cohort'].value_counts().to_dict()}")

    # 2. Load the raw PyPI weekly panel
    # Note: We need to use the .venv/bin/python to run this or ensure pyarrow is available.
    # Since I'm writing the script to be run via the CLI, I'll assume pyarrow is in the environment.
    pypi_path = RAW_DIR / "pypi_downloads.parquet"
    df_panel = pd.read_parquet(pypi_path, columns=["project", "week_start", "downloads"])
    df_panel["package"] = normalize_name(df_panel["project"])
    df_panel["week_start"] = pd.to_datetime(df_panel["week_start"])

    # 3. Merge and Filter
    df_plot = df_panel.merge(df_meta[["package", "cohort"]], on="package", how="inner")

    # Side-by-side mode: median (typical package) vs mean (aggregate volume).
    # The contrast surfaces outlier dependence (e.g. mdurl drives the July mean).
    if args.side_by_side:
        agg_med = (df_plot.groupby(["week_start", "cohort"])["downloads"]
                   .median().reset_index())
        agg_mean = (df_plot.groupby(["week_start", "cohort"])["downloads"]
                    .mean().reset_index())

        cutoff_date = CUTOFFS[MAIN_CUTOFF_NAME]
        fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), sharex=True)

        for ax, agg_df, title, ylab, annot in [
            (axes[0], agg_med,
             "Median Weekly Downloads (Typical Package)",
             "Median Weekly Downloads (Log Scale)",
             "Cohorts converge\n(no typical-package gap)"),
            (axes[1], agg_mean,
             "Mean Weekly Downloads (Aggregate Volume)",
             "Mean Weekly Downloads (Log Scale)",
             "Gap driven by mdurl\n(3B post-AI downloads, July cohort)"),
        ]:
            sns.lineplot(data=agg_df, x="week_start", y="downloads",
                         hue="cohort", ax=ax, linewidth=1.8)
            ax.axvline(cutoff_date, color="grey", linestyle="--", alpha=0.7,
                       label="Knowledge Cutoff (Sept 2021)")
            ax.axvline(CHATGPT_RELEASE, color="red", linestyle="-", alpha=0.8,
                       label="ChatGPT Release (Nov 2022)")
            ax.axvline(GPT4_RELEASE, color="darkred", linestyle=":", alpha=0.8,
                       label="GPT-4 Release (March 2023)")
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("Calendar Date")
            ax.set_ylabel(ylab)
            ax.set_yscale("log")
            ymax = agg_df["downloads"].max()
            ax.text(pd.Timestamp("2023-07-01"), ymax * 0.35, annot,
                    fontweight="bold",
                    bbox=dict(facecolor="white", alpha=0.7, edgecolor="grey"))
            ax.legend(title="Library Cohort", loc="upper left", fontsize=8)

        fig.suptitle(
            "Long-Horizon Diffusion: Median vs Mean for July (Pre-Cutoff) and October (Post-Cutoff) 2021 Cohorts",
            fontweight="bold", fontsize=12)
        plt.tight_layout()
        out_path = FIG_MAIN / "long_horizon_trajectory_pypi_median_vs_mean.png"
        plt.savefig(out_path, dpi=300)
        print(f"Saved side-by-side median-vs-mean plot to {out_path}")
        return

    # 4. Aggregate Weekly Averages
    # We use median or log-mean to handle skewness, but your supervisor asked for "cumulative use"
    # so let's show the Average Weekly Downloads to see the growth rates.
    agg = df_plot.groupby(["week_start", "cohort"])["downloads"].mean().reset_index()
    
    # Calculate Cumulative Average for the "All-time" perspective
    agg = agg.sort_values(["cohort", "week_start"])
    agg["cum_avg_downloads"] = agg.groupby("cohort")["downloads"].cumsum()

    # 5. Plotting
    fig, ax = plt.subplots(figsize=(12, 7))
    
    sns.lineplot(data=agg, x="week_start", y="downloads", hue="cohort", ax=ax, linewidth=2)
    
    # Add Milestones
    cutoff_date = CUTOFFS[MAIN_CUTOFF_NAME]
    ax.axvline(cutoff_date, color="grey", linestyle="--", alpha=0.7, label="Knowledge Cutoff (Sept 2021)")
    ax.axvline(CHATGPT_RELEASE, color="red", linestyle="-", alpha=0.8, label="ChatGPT Release (Nov 2022)")
    ax.axvline(GPT4_RELEASE, color="darkred", linestyle=":", alpha=0.8, label="GPT-4 Release (March 2023)")

    ax.set_title("The Long-Horizon Diffusion Gap: July vs. October 2021 Cohorts", fontweight='bold')
    ax.set_ylabel("Average Weekly Downloads (Log Scale)")
    ax.set_xlabel("Calendar Date")
    ax.set_yscale("log")
    
    ax.legend(title="Library Cohort", loc="upper left")
    
    # Annotate the gap
    if trim_top_pct is not None:
        ax.text(pd.Timestamp("2023-06-01"), agg["downloads"].max() * 0.4,
                "Oct > July\n(after ChatGPT)",
                color="black", fontweight="bold", bbox=dict(facecolor='white', alpha=0.5))
    else:
        ax.text(pd.Timestamp("2024-06-01"), 1000, "Persistence of Gap\n(No Catch-up)",
                color="black", fontweight="bold", bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout()
    suffix = f"_trimmed_top{trim_top_pct:.0f}pct" if trim_top_pct is not None else ""
    out_path = FIG_MAIN / f"long_horizon_trajectory_pypi{suffix}.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved trajectory plot to {out_path}")

    # 6. Cumulative Plot (The "Total Use" View)
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    sns.lineplot(data=agg, x="week_start", y="cum_avg_downloads", hue="cohort", ax=ax2, linewidth=2)
    
    ax2.axvline(cutoff_date, color="grey", linestyle="--", alpha=0.7)
    ax2.axvline(CHATGPT_RELEASE, color="red", linestyle="-", alpha=0.8, label="ChatGPT Release")
    
    ax2.set_title("Cumulative Diffusion Advantage (All-Time)", fontweight='bold')
    ax2.set_ylabel("Cumulative Average Downloads")
    ax2.set_xlabel("Calendar Date")
    ax2.set_yscale("log")
    
    plt.tight_layout()
    out_path_cum = FIG_MAIN / "long_horizon_cumulative_pypi.png"
    plt.savefig(out_path_cum, dpi=300)
    print(f"Saved cumulative plot to {out_path_cum}")

if __name__ == "__main__":
    main()
