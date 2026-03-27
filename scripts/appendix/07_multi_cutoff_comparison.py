import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from config import FINAL_DIR, RESULTS_DIR, CUTOFFS, DONUT_WEEKS
from utils import run_local_linear_rdd

def main():
    outcome = "total_downloads_52wk"
    final_results = []
    
    print(f"Comparing RDD estimates across cutoffs for {outcome}...")
    for name in CUTOFFS.keys():
        df_path = FINAL_DIR / f"analysis_{name}.csv"
        if not df_path.exists():
            continue
        df = pd.read_csv(df_path)
        
        # Test No-Donut and Donut
        final_results.append(run_local_linear_rdd(df, outcome, h=26, donut_weeks=None, label=name, cluster_col="dist_to_cutoff"))
        final_results.append(run_local_linear_rdd(df, outcome, h=26, donut_weeks=DONUT_WEEKS, label=f"{name} (Donut)", cluster_col="dist_to_cutoff"))
            
    res_df = pd.DataFrame(final_results)
    print("\n=========================================")
    print("      MULTI-CUTOFF COMPARISON RESULTS    ")
    print("=========================================\n")
    print(res_df.round(4).to_string(index=False))
    
    res_df.to_csv(RESULTS_DIR / "multi_cutoff_comparison.csv", index=False)

if __name__ == "__main__":
    main()
