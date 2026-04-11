import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import FINAL_DIR, RESULTS_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, run_quantile_rdd, setup_plotting_style

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()
    
    # 1. Load and Pool Placebo Cutoffs (2018, 2019, 2020)
    placebos = ["Placebo_2018", "Placebo_2019", "Placebo_2020"]
    pooled_list = []
    
    for p in placebos:
        path = FINAL_DIR / f"analysis_{p}.csv"
        if path.exists():
            tmp = pd.read_csv(path)
            tmp["cutoff_year"] = p
            tmp["is_main_2021"] = 0
            pooled_list.append(tmp)
            
    # Add 2021 for comparison
    main_path = FINAL_DIR / "analysis_Main_2021.csv"
    if main_path.exists():
        tmp_main = pd.read_csv(main_path)
        tmp_main["cutoff_year"] = "Main_2021"
        tmp_main["is_main_2021"] = 1
        pooled_list.append(tmp_main)
        
    df_stack = pd.concat(pooled_list, ignore_index=True)
    df_stack_min10 = df_stack[df_stack["total_downloads_52wk"] >= 10].copy()
    
    # 2. Estimate Average Placebo Jump (Log Mean)
    print("Estimating Average Placebo Jump (2018-2020)...")
    df_placebo_pool = df_stack_min10[df_stack_min10["is_main_2021"] == 0].copy()
    res_placebo_mean = run_local_linear_rdd(df_placebo_pool, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label="Stacked Placebos (Mean)", cluster_col="dist_to_cutoff")
    
    # 3. Estimate Average Placebo Jump (Median)
    print("Estimating Average Placebo Jump (Median)...")
    res_placebo_median = run_quantile_rdd(df_placebo_pool, "total_downloads_52wk", q=0.5, h=26, donut_weeks=DONUT_WEEKS, label="Stacked Placebos (Median)")
    
    # 4. Compare with 2021
    print("Estimating 2021 Main Jump for comparison...")
    df_main = df_stack_min10[df_stack_min10["is_main_2021"] == 1].copy()
    res_main_mean = run_local_linear_rdd(df_main, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label="Main 2021 (Mean)", cluster_col="dist_to_cutoff")
    res_main_median = run_quantile_rdd(df_main, "total_downloads_52wk", q=0.5, h=26, donut_weeks=DONUT_WEEKS, label="Main 2021 (Median)")
    
    # Compile Results
    results = [res_placebo_mean, res_placebo_median, res_main_mean, res_main_median]
    res_df = pd.DataFrame(results)
    
    print("\n=========================================")
    print("      STACKED RDD ANALYSIS RESULTS       ")
    print("=========================================\n")
    print(res_df[["Label", "Estimate", "Std.Err", "P-value", "N"]].round(4).to_string(index=False))
    
    # 5. Visual Comparison
    plt.figure(figsize=(10, 6))
    plt.errorbar(res_df["Label"], res_df["Estimate"], yerr=res_df["Std.Err"]*1.96, fmt='o', capsize=5)
    plt.axhline(0, color='red', linestyle='--')
    plt.title("Stacked Placebo Jump vs. 2021 Main Jump")
    plt.ylabel("Estimate")
    plt.xticks(rotation=15)
    plt.savefig(RESULTS_DIR / "figures" / "stacked_rdd_comparison.png")
    
    res_df.to_csv(RESULTS_DIR / "stacked_rdd_results.csv", index=False)
    print(f"\nSaved results to: {RESULTS_DIR / 'stacked_rdd_results.csv'}")

if __name__ == "__main__":
    main()
