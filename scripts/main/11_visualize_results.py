import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import MAIN_ANALYSIS_DATA, FINAL_DIR, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS, CHATGPT_RELEASE, RAW_DIR, CUTOFFS, MAIN_CUTOFF_NAME
from utils import setup_plotting_style, normalize_name

def plot_long_horizon_trajectory():
    """Visualizes the 2021 cohort divergence using raw panel data (Activation Plot)."""
    if not MAIN_ANALYSIS_DATA.exists(): 
        print(f"Skipping trajectory plot: {MAIN_ANALYSIS_DATA} not found.")
        return
    
    # 1. Load the cross-sectional analysis file for cohort assignment
    df_meta = pd.read_csv(MAIN_ANALYSIS_DATA, usecols=["package", "dist_to_cutoff"])
    
    # Define July vs October cohorts based on dist_to_cutoff (h=13 window)
    df_meta["cohort"] = "Other"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= -12) & (df_meta["dist_to_cutoff"] <= -9), "cohort"] = "July 2021 (Pre-Cutoff)"
    df_meta.loc[(df_meta["dist_to_cutoff"] >= 1) & (df_meta["dist_to_cutoff"] <= 4), "cohort"] = "October 2021 (Post-Cutoff)"
    
    df_meta = df_meta[df_meta["cohort"] != "Other"].copy()
    
    # 2. Load the raw PyPI weekly panel
    pypi_path = RAW_DIR / "pypi_downloads.parquet"
    if not pypi_path.exists():
        print(f"Skipping trajectory plot: {pypi_path} not found.")
        return
        
    df_panel = pd.read_parquet(pypi_path, columns=["project", "week_start", "downloads"])
    df_panel["package"] = normalize_name(df_panel["project"])
    df_panel["week_start"] = pd.to_datetime(df_panel["week_start"])

    # 3. Merge and Aggregate
    df_plot = df_panel.merge(df_meta[["package", "cohort"]], on="package", how="inner")
    agg = df_plot.groupby(["week_start", "cohort"])["downloads"].mean().reset_index()
    
    # 4. Plotting
    setup_plotting_style()
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=agg, x="week_start", y="downloads", hue="cohort", linewidth=2)
    
    # Add Milestones
    plt.axvline(CUTOFFS[MAIN_CUTOFF_NAME], color="grey", linestyle="--", alpha=0.7, label="Knowledge Cutoff")
    plt.axvline(CHATGPT_RELEASE, color="red", linestyle="-", alpha=0.8, label="ChatGPT Release")
    
    plt.title("Long-Horizon Adoption Trajectory: July vs. October 2021 Cohorts", fontsize=14)
    plt.xlabel("Calendar Date", fontsize=12)
    plt.ylabel("Average Weekly Downloads (Log Scale)", fontsize=12)
    plt.yscale("log")
    plt.legend(title="Library Cohort", loc="upper left")
    
    plt.savefig(FIGURES_DIR / "long_horizon_trajectory_pypi.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_suppression_visual():
    """Visualizes the 'Missing Boost' by comparing 2021 against historical placebos."""
    results_path = RESULTS_DIR / "diff_in_rdd_tiers.csv"
    if not results_path.exists(): 
        print(f"Skipping suppression visual: {results_path} not found.")
        return
    
    # Plotting the 'Excess Jump' coefficients across tiers
    df = pd.read_csv(results_path)
    setup_plotting_style()
    plt.figure(figsize=(8, 6))
    sns.barplot(data=df, x="Tier", y="Excess_Jump", palette="RdYlGn_r", hue="Tier", legend=False)
    plt.axhline(0, color='black', linewidth=1)
    plt.title("The 'Cutoff Tax': Seasonal Suppression by Success Tier", fontsize=14)
    plt.ylabel("Excess Jump (Log Points relative to Placebos)", fontsize=12)
    plt.xticks(rotation=15)
    plt.savefig(FIGURES_DIR / "suppression_visual_success_tiers.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_horizon_coefficients():
    """Plots RDD estimates across different time horizons."""
    results_path = RESULTS_DIR / "estimation_results_final.csv"
    if not results_path.exists(): return
    df = pd.read_csv(results_path)
    
    # Filter for Broad tier and specific PyPI outcomes
    horizons = ["total_downloads_52wk", "cum_downloads_gpt4", "cum_downloads_gpt4turbo", "cum_downloads_alltime"]
    h_df = df[(df["Label"].str.contains("Broad")) & (df["Outcome"].isin(horizons))].copy()
    
    if h_df.empty: return
    
    plt.figure(figsize=(8, 6))
    plt.errorbar(range(len(h_df)), h_df["Estimate"], yerr=h_df["Std.Err"] * 1.96, fmt='o-', capsize=5)
    plt.axhline(0, color='red', linestyle='--')
    plt.xticks(range(len(h_df)), ["52wk", "GPT-4", "Turbo", "All-Time"])
    plt.title("RDD Estimates across Adoption Horizons (Broad Tier)")
    plt.savefig(FIGURES_DIR / "rdd_horizon_coefficients.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()
    plot_long_horizon_trajectory()
    plot_suppression_visual()
    plot_horizon_coefficients()
    print(f"Finalized visualizations saved to {FIGURES_DIR}")
