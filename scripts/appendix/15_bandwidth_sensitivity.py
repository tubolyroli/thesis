import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS, MIN_DOWNLOADS_FILTER, BW_GRID
from utils import run_rdrobust_est, setup_plotting_style

def main():
    setup_plotting_style()
    FIGURES_DIR = RESULTS_DIR / "figures"
    
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    print("Loading data for bandwidth sensitivity...")
    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_min10 = df_full[df_full["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
    
    outcome = "post_ai_downloads_alltime"
    # Bandwidths to test (in weeks from cutoff)
    bandwidths = BW_GRID
    
    results = []
    print(f"Running sensitivity for {outcome}...")
    
    for h in bandwidths:
        print(f"  Testing Bandwidth: {h} weeks...")
        res = run_rdrobust_est(df_min10, outcome, h=h, donut_weeks=DONUT_WEEKS, label=f"BW: {h}w")
        results.append(res)

    results_df = pd.DataFrame(results)
    results_df["BW"] = bandwidths
    
    # Save the table
    results_df.to_csv(RESULTS_DIR / "sensitivity_bandwidth_post_ai.csv", index=False)
    print(f"Saved sensitivity results to {RESULTS_DIR / 'sensitivity_bandwidth_post_ai.csv'}")

    # Plot Sensitivity
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Conventional confidence intervals (95%)
    # Using 1.96 * Std.Err as a proxy for the Robust CI provided by rdrobust
    ax.errorbar(results_df["BW"], results_df["Estimate"], 
                yerr=1.96 * results_df["Std.Err"], 
                fmt='o-', capsize=5, label="Estimate (95% CI)")
    
    ax.axhline(0, color='red', linestyle='--')
    ax.set_title(f"Bandwidth Sensitivity: {outcome}", fontsize=14, fontweight='bold')
    ax.set_xlabel("Bandwidth (Weeks from Cutoff)", fontsize=12)
    ax.set_ylabel("RDD Estimate", fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = FIGURES_DIR / "sensitivity_bandwidth_post_ai.png"
    plt.savefig(plot_path, dpi=300)
    print(f"Saved sensitivity plot to {plot_path}")

    print("\n=========================================")
    print("     BANDWIDTH SENSITIVITY SUMMARY       ")
    print("=========================================\n")
    print(results_df[["BW", "Estimate", "Std.Err", "P-value", "N"]].round(4).to_string(index=False))

if __name__ == "__main__":
    main()
