import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import RAW_DIR, FINAL_DIR, RESULTS_DIR, CHATGPT_RELEASE, GPT4_RELEASE, MAIN_CUTOFF_NAME, DONUT_WEEKS, CUTOFFS
from utils import setup_plotting_style, normalize_name

def main():
    setup_plotting_style()
    FIGURES_DIR = RESULTS_DIR / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading datasets for trajectory visualization...")
    # 1. Load the cross-sectional analysis file for cohort assignment
    df_meta = pd.read_csv(FINAL_DIR / "analysis_Main_2021.csv", usecols=["package", "dist_to_cutoff", "release_week"])
    
    # Define July vs October cohorts based on dist_to_cutoff
    # Donut is -8 to 0 (Aug/Sept). 
    # July: -12 to -9
    # October: 1 to 4
    df_meta["cohort"] = "Other"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= -12) & (df_meta["dist_to_cutoff"] <= -9), "cohort"] = "July 2021 (Pre-Cutoff)"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= 1) & (df_meta["dist_to_cutoff"] <= 4), "cohort"] = "October 2021 (Post-Cutoff)"
    
    df_meta = df_meta[df_meta["cohort"] != "Other"].copy()
    print(f"  Cohort sizes: {df_meta['cohort'].value_counts().to_dict()}")

    # 2. Load the raw PyPI weekly panel
    # Note: We need to use the .venv/bin/python to run this or ensure pyarrow is available.
    # Since I'm writing the script to be run via the CLI, I'll assume pyarrow is in the environment.
    pypi_path = RAW_DIR / "pypi_downloads.parquet"
    df_panel = pd.read_parquet(pypi_path, columns=["project", "week_start", "downloads"])
    df_panel["package"] = normalize_name(df_panel["project"])
    df_panel["week_start"] = pd.to_datetime(df_panel["week_start"])

    # 3. Merge and Filter
    df_plot = df_panel.merge(df_meta[["package", "cohort"]], on="package", how="inner")
    
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
    ax.text(pd.Timestamp("2024-06-01"), 1000, "Persistence of Gap\n(No Catch-up)", 
            color="black", fontweight="bold", bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout()
    out_path = FIGURES_DIR / "long_horizon_trajectory_pypi.png"
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
    out_path_cum = FIGURES_DIR / "long_horizon_cumulative_pypi.png"
    plt.savefig(out_path_cum, dpi=300)
    print(f"Saved cumulative plot to {out_path_cum}")

if __name__ == "__main__":
    main()
