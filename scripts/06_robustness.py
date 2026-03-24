import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import FINAL_DIR, RESULTS_DIR, CUTOFFS, DONUT_WEEKS, DEFAULT_BW, MIN_DOWNLOADS_FILTER
from utils import run_rdrobust_est, run_quantile_rdd, setup_plotting_style

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()
    
    robust_results = []
    
    # 1. Placebo Cutoffs (Like-for-Like relative to release)
    print("Running Placebo Sensitivity (Outcome: total_downloads_52wk)...")
    for name, date in CUTOFFS.items():
        if "Placebo" in name:
            df_path = FINAL_DIR / f"analysis_{name}.csv"
            if df_path.exists():
                df = pd.read_csv(df_path)
                # Baseline filter
                df_min10 = df[df["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
                
                print(f"  Estimating Placebo: {name} (Outcome: total_downloads_52wk)...")
                res = run_rdrobust_est(
                    df_min10, "total_downloads_52wk", h=DEFAULT_BW, 
                    donut_weeks=DONUT_WEEKS, label=f"Placebo: {name}"
                )
                robust_results.append(res)

    # 2. Median RDD (Robust to outliers)
    print("\nRunning Median RDD for Main 2021 (Post-AI Horizon)...")
    main_df_path = FINAL_DIR / "analysis_Main_2021.csv"
    if main_df_path.exists():
        df_main = pd.read_csv(main_df_path)
        df_min10 = df_main[df_main["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
        
        # Test Median for Post-AI Downloads (The primary "Activation" outcome)
        print("  Estimating Median RDD...")
        res_median = run_quantile_rdd(
            df_min10, "post_ai_downloads_alltime", q=0.5, h=DEFAULT_BW, 
            donut_weeks=DONUT_WEEKS, label="Main: Median RDD (Post-AI)"
        )
        robust_results.append(res_median)

    # 3. Symmetric Donut Sensitivity (±4 weeks)
    # The primary design is asymmetric (excl. Aug-Sept).
    # This robustness test uses a standard symmetric donut.
    print("\nRunning Main 2021 with Symmetric Donut (±4 weeks)...")
    if main_df_path.exists():
        df_main = pd.read_csv(main_df_path)
        df_min10 = df_main[df_main["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
        
        SYMMETRIC_DONUT = list(range(-4, 5)) # Weeks -4 to +4
        print(f"  Estimating Main (h={DEFAULT_BW}, Symmetric Donut: ±4w)...")
        res_sym = run_rdrobust_est(
            df_min10, "post_ai_downloads_alltime", h=DEFAULT_BW, 
            donut_weeks=SYMMETRIC_DONUT, label="Main: Symmetric Donut (±4w)"
        )
        robust_results.append(res_sym)

    # Compile and Save
    robust_df = pd.DataFrame(robust_results)
    out_path = RESULTS_DIR / "robustness_placebo_median_summary.csv"
    robust_df.to_csv(out_path, index=False)
    
    print("\n=========================================")
    print("      ROBUSTNESS & PLACEBO RESULTS       ")
    print("=========================================\n")
    print(robust_df[["Label", "Outcome", "Estimate", "Std.Err", "P-value", "N"]].round(4).to_string(index=False))
    print(f"\nSaved robustness results to {out_path}")

if __name__ == "__main__":
    main()
