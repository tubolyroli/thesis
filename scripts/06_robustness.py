import pandas as pd
import matplotlib.pyplot as plt
from config import MAIN_ANALYSIS_DATA, FIGURES_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, setup_plotting_style

def main():
    setup_plotting_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MAIN_ANALYSIS_DATA.exists():
        return

    df = pd.read_csv(MAIN_ANALYSIS_DATA)
    outcome = "total_downloads_52wk"
    
    # 1. Bandwidth Sensitivity
    print("Running Bandwidth Sensitivity Test...")
    bw_results = []
    for h in range(10, 53, 2):
        res = run_local_linear_rdd(df, outcome, h=h, donut_weeks=DONUT_WEEKS, cluster_col="dist_to_cutoff")
        bw_results.append(res)
        
    bw_df = pd.DataFrame(bw_results)
    
    plt.figure()
    plt.axhline(0, color='red', linestyle='--')
    plt.errorbar(bw_df["BW"], bw_df["Estimate"], yerr=1.96*bw_df["Std.Err"], fmt='o', color='steelblue', capsize=5)
    plt.title(f"Bandwidth Sensitivity: {outcome}")
    plt.xlabel("Bandwidth (Weeks)")
    plt.ylabel("RDD Estimate")
    plt.savefig(FIGURES_DIR / "robustness_bw_sensitivity.png")
    plt.close()
    
    # 2. Placebo Cutoffs (Shift within window)
    print("Running Placebo Cutoff Tests (±10 weeks)...")
    placebos = [-10, -5, 5, 10]
    placebo_results = []
    
    for p in placebos:
        df_p = df.copy()
        df_p["dist_to_cutoff"] = df_p["dist_to_cutoff"] - p
        res = run_local_linear_rdd(df_p, outcome, h=26, donut_weeks=None, label=f"Shift: {p}")
        placebo_results.append(res)
        
    print("\nPlacebo Results:")
    print(pd.DataFrame(placebo_results).round(4).to_string(index=False))

if __name__ == "__main__":
    main()
