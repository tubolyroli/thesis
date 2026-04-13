import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import RESULTS_DIR, FIGURES_DIR
from utils import setup_plotting_style

def plot_suppression_visual():
    """Visualizes the 'Missing Boost' by comparing 2021 against historical placebos."""
    results_path = RESULTS_DIR / "diff_in_rdd_tiers.csv"
    if not results_path.exists(): 
        print(f"Skipping suppression visual: {results_path} not found.")
        return
    
    # Plotting the 'Excess Jump' coefficients across tiers (adjusted = primary)
    df = pd.read_csv(results_path)
    if "Baseline_Adjusted" in df.columns:
        # Prefer adjusted; fall back to unadjusted for outcomes where adjusted is unavailable
        adj = df[df["Baseline_Adjusted"] == True]
        unadj_only = df[(df["Baseline_Adjusted"] == False) & (~df["Outcome"].isin(adj["Outcome"].values))]
        df = pd.concat([adj, unadj_only])
    # Clean up tick labels: replace shorthand with human-readable text
    tier_map = {
        "Successful (min500@26w)": "Successful (min 500 at 26w)",
        "Superstar (min1000@26w)": "Superstar (min 1000 at 26w)",
    }
    df["Tier"] = df["Tier"].replace(tier_map)
    setup_plotting_style()
    plt.figure(figsize=(8, 6))
    sns.barplot(data=df, x="Tier", y="Excess_Jump", palette="RdYlGn_r", hue="Tier", legend=False)
    plt.axhline(0, color='black', linewidth=1)
    plt.title("The 'Cutoff Tax': Seasonal Suppression by Success Tier", fontsize=14)
    plt.ylabel("Excess Jump (relative to placebo average)", fontsize=12)
    plt.xticks(rotation=15)
    plt.savefig(FIGURES_DIR / "suppression_visual_success_tiers.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_horizon_coefficients():
    """Plots RDD estimates across different time horizons."""
    results_path = RESULTS_DIR / "estimation_results_final.csv"
    if not results_path.exists(): return
    df = pd.read_csv(results_path)
    
    # Filter for Broad tier, Fixed h=13, and specific PyPI outcomes
    horizons = ["total_downloads_52wk", "cum_downloads_gpt4", "cum_downloads_gpt4turbo", "cum_downloads_alltime"]
    h_df = df[(df["Label"].str.contains("Broad")) & (df["Label"].str.contains("Fixed")) & (df["Outcome"].isin(horizons))].copy()
    # If Baseline_Adjusted column exists, keep adjusted where available, unadjusted otherwise
    if "Baseline_Adjusted" in h_df.columns:
        adj = h_df[h_df["Baseline_Adjusted"] == "Yes"]
        unadj_only = h_df[(h_df["Baseline_Adjusted"] == "No") & (~h_df["Outcome"].isin(adj["Outcome"].values))]
        h_df = pd.concat([adj, unadj_only]).sort_values("Outcome")
    
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
    plot_suppression_visual()
    plot_horizon_coefficients()
    print(f"Finalized visualizations saved to {FIGURES_DIR}")
