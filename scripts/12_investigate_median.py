import pandas as pd
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, DONUT_WEEKS
from utils import run_quantile_rdd

def main():
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df_full = pd.read_csv(MAIN_ANALYSIS_DATA)
    df_min10 = df_full[df_full["total_downloads_52wk"] >= 10].copy()
    
    print("Investigating Distributional Effects (Quantile RDD)...")
    quantiles = [0.25, 0.5, 0.75, 0.90]
    results = []
    
    for q in quantiles:
        print(f"  Running RDD for Quantile: {q}")
        res = run_quantile_rdd(df_min10, "total_downloads_52wk", q=q, h=26, donut_weeks=DONUT_WEEKS, label=f"Quantile: {q}")
        results.append(res)
        
    results_df = pd.DataFrame(results)
    print("\n=========================================")
    print("      DISTRIBUTIONAL RDD RESULTS        ")
    print("=========================================\n")
    print(results_df[["Label", "Estimate", "Std.Err", "P-value", "N"]].round(4).to_string(index=False))
    
    results_df.to_csv(RESULTS_DIR / "quantile_investigation.csv", index=False)

if __name__ == "__main__":
    main()
