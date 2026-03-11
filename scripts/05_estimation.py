import pandas as pd
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, run_rdrobust_est, run_quantile_rdd

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_min10 = df_full[df_full["total_downloads_52wk"] >= 10].copy()
    results = []
    
    # 1. Horizon Analysis (Catch-up check)
    print("Running Horizon Analysis (Catch-up check)...")
    horizons = [12, 26, 52]
    for h_weeks in horizons:
        outcome = f"cum_downloads_{h_weeks}wk"
        results.append(run_rdrobust_est(df_min10, outcome, h=26, donut_weeks=DONUT_WEEKS, label=f"Horizon: {h_weeks}w Downloads"))

    # 2. Distributional Analysis (Quantile RDD)
    print("Running Distributional Analysis (Quantile RDD)...")
    quantiles = [0.25, 0.5, 0.75, 0.90]
    for q in quantiles:
        results.append(run_quantile_rdd(df_min10, "total_downloads_52wk", q=q, h=26, donut_weeks=DONUT_WEEKS, label=f"Quantile: {q}"))

    # 3. GitHub Margin Splits
    print("Running GitHub Margins...")
    df_gh = df_full[df_full["total_downloads_52wk"] >= 10].copy()
    results.append(run_rdrobust_est(df_gh, "matched_to_github", h=26, donut_weeks=DONUT_WEEKS, label="GitHub: Match Probability"))
    
    df_matched = df_gh[df_gh["matched_to_github"] == 1].copy()
    for h_weeks in horizons:
        outcome = f"cum_imports_{h_weeks}wk"
        results.append(run_rdrobust_est(df_matched, outcome, h=26, donut_weeks=DONUT_WEEKS, label=f"GitHub: {h_weeks}w Log Imports (Cond)"))

    # Compile and Save
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "estimation_results_final.csv", index=False)
    
    print("\n=========================================")
    print("      FINAL RDD ESTIMATION RESULTS       ")
    print("=========================================\n")
    print(results_df[["Label", "Outcome", "Estimate", "Std.Err", "P-value", "Method", "N"]].round(4).to_string(index=False))
    print(f"\nSaved final results to: {RESULTS_DIR / 'estimation_results_final.csv'}")

if __name__ == "__main__":
    main()
