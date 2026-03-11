import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, setup_plotting_style, run_quantile_rdd

def run_bandwidth_sensitivity_median():
    """Tests the stability of the Median RDD result across different bandwidths."""
    if not MAIN_ANALYSIS_DATA.exists(): return
    
    df = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_min10 = df[df["total_downloads_52wk"] >= 10].copy()
    
    bandwidths = [12, 16, 20, 26, 30, 40, 52]
    results = []
    
    print("Running Bandwidth Sensitivity for Median RDD...")
    for h in bandwidths:
        res = run_quantile_rdd(df_min10, "total_downloads_52wk", q=0.5, h=h, donut_weeks=DONUT_WEEKS, label=f"h={h}")
        results.append(res)
        
    res_df = pd.DataFrame(results)
    setup_plotting_style()
    plt.figure(figsize=(10, 6))
    plt.errorbar(res_df["BW"], res_df["Estimate"], yerr=res_df["Std.Err"]*1.96, fmt='o-', capsize=5)
    plt.axhline(0, color='red', linestyle='--')
    plt.title("Median RDD (q=0.5): Bandwidth Sensitivity")
    plt.xlabel("Bandwidth (Weeks)")
    plt.ylabel("Estimated Discontinuity (Downloads)")
    
    out_path = FIGURES_DIR / "median_rdd_bandwidth_sensitivity.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved Median RDD sensitivity plot to: {out_path}")

def run_placebo_cutoffs_median():
    """Tests Median RDD on placebo cutoff dates."""
    if not MAIN_ANALYSIS_DATA.exists(): return
    
    df = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_min10 = df[df["total_downloads_52wk"] >= 10].copy()
    
    # Simple shift placebos
    shifts = [-20, -15, -10, 10, 15, 20]
    results = []
    
    print("Running Placebo Cutoff Tests for Median RDD...")
    for s in shifts:
        df_p = df_min10.copy()
        df_p["dist_to_cutoff"] = df_p["dist_to_cutoff"] - s
        res = run_quantile_rdd(df_p, "total_downloads_52wk", q=0.5, h=26, donut_weeks=DONUT_WEEKS, label=f"Shift: {s}")
        results.append(res)
        
    print("\nMedian RDD Placebo Results:")
    print(pd.DataFrame(results)[["Label", "Estimate", "Std.Err", "P-value"]].to_string(index=False))

def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    run_bandwidth_sensitivity_median()
    run_placebo_cutoffs_median()

if __name__ == "__main__":
    main()
