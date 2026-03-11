import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import FINAL_DIR, RESULTS_DIR, DONUT_WEEKS

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load 2020 and 2021 datasets
    p_2020 = FINAL_DIR / "analysis_Placebo_2020.csv"
    p_2021 = FINAL_DIR / "analysis_Main_2021.csv"
    
    if not (p_2020.exists() and p_2021.exists()):
        print("Required analysis files for 2020 or 2021 not found.")
        return

    df_2020 = pd.read_csv(p_2020)
    df_2021 = pd.read_csv(p_2021)
    
    # 2. Prep
    df_2020["is_2021"] = 0
    df_2021["is_2021"] = 1
    df = pd.concat([df_2020, df_2021], ignore_index=True)
    
    h = 26
    df = df[~df["dist_to_cutoff"].isin(DONUT_WEEKS)]
    df = df[(df["dist_to_cutoff"] >= -h) & (df["dist_to_cutoff"] <= h)].copy()
    
    df["log_y"] = np.log1p(df["total_downloads_52wk"])
    df["x"] = df["dist_to_cutoff"]
    df["pre"] = (df["x"] < 0).astype(int)
    df["weight"] = 1 - (np.abs(df["x"]) / h)
    
    # 3. Diff-in-RDD Specification
    formula = "log_y ~ pre * is_2021 + x * pre * is_2021"
    
    print("Estimating Diff-in-RDD (2020 Placebo vs 2021 Main)...")
    # Using week-clustered SEs as primary inference for Diff-in-RDD
    # Statsmodels clustering requires non-negative integer groups
    df['cluster_idx'] = df["dist_to_cutoff"].astype('category').cat.codes
    model = smf.wls(formula, data=df, weights=df["weight"]).fit(cov_type='cluster', cov_kwds={'groups': df["cluster_idx"]})
    
    coef = model.params["pre:is_2021"]
    se = model.bse["pre:is_2021"]
    pval = model.pvalues["pre:is_2021"]
    
    print("\n=========================================")
    print("      DIFF-IN-RDD ESTIMATION RESULTS     ")
    print("=========================================\n")
    print(f"Outcome: log(1 + 52w Downloads)")
    print(f"Diff-in-Jumps Coefficient: {coef:.4f}")
    print(f"P-value:                  {pval:.4f}")
    
    with open(RESULTS_DIR / "diff_in_rdd_summary.txt", "w") as f:
        f.write(model.summary().as_text())

if __name__ == "__main__":
    main()
