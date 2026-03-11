import pandas as pd
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, run_rdrobust_est

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    results = []
    
    # 1. Main Outcome (Downloads) across Sample Thresholds
    print("Running Table 2: Main RD estimates (Downloads) across sample thresholds...")
    thresholds = {"Full": 0, "min10": 10, "min100": 100}
    
    for label, thresh in thresholds.items():
        sub = df_full[df_full["total_downloads_52wk"] >= thresh].copy()
        # Primary: rdrobust
        results.append(run_rdrobust_est(sub, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label=f"Table 2: {label} (rdrobust)"))
        # Sensitivity: WLS + HC1
        results.append(run_local_linear_rdd(sub, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label=f"Table 3: {label} (WLS HC1)"))
        # Sensitivity: WLS + Week Clustered
        results.append(run_local_linear_rdd(sub, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label=f"Table 3: {label} (WLS Clustered)", cluster_col="dist_to_cutoff"))

    # 2. GitHub Margin Splits (Table 4)
    print("Running Table 4: GitHub Margins...")
    # Use min10 sample for GitHub outcomes as base
    df_gh = df_full[df_full["total_downloads_52wk"] >= 10].copy()
    
    # Extensive margin 1: Match Probability
    results.append(run_rdrobust_est(df_gh, "matched_to_github", h=26, donut_weeks=DONUT_WEEKS, label="Table 4: Matched to GitHub"))
    
    # Intensive margin: Log Imports (Conditional on match)
    df_matched = df_gh[df_gh["matched_to_github"] == 1].copy()
    results.append(run_rdrobust_est(df_matched, "cum_imports_52wk", h=26, donut_weeks=DONUT_WEEKS, label="Table 4: Log Imports (Cond)"))

    # Compile and Save
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "estimation_results.csv", index=False)
    
    print("\n=========================================")
    print("      REVISED RDD ESTIMATION RESULTS     ")
    print("=========================================\n")
    print(results_df[["Label", "Outcome", "Estimate", "Std.Err", "P-value", "Method", "N"]].round(4).to_string(index=False))
    print(f"\nSaved results to: {RESULTS_DIR / 'estimation_results.csv'}")

if __name__ == "__main__":
    main()
