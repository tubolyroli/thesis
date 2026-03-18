import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import FINAL_DIR, RESULTS_DIR, DONUT_WEEKS

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load 2018, 2019, 2020 (Placebos) and 2021 (Main) datasets
    placebos = ["Placebo_2018", "Placebo_2019", "Placebo_2020"]
    main_cutoff = "Main_2021"
    
    dfs = []
    
    # Load Main 2021
    main_path = FINAL_DIR / f"analysis_{main_cutoff}.csv"
    if main_path.exists():
        df_main = pd.read_csv(main_path)
        df_main["is_2021"] = 1
        dfs.append(df_main)
    
    # Load Placebos
    for p in placebos:
        p_path = FINAL_DIR / f"analysis_{p}.csv"
        if p_path.exists():
            df_p = pd.read_csv(p_path)
            df_p["is_2021"] = 0
            dfs.append(df_p)
            
    if len(dfs) < 2:
        print("Required analysis files for Diff-in-RDD not found.")
        return

    # Pool all years
    df = pd.concat(dfs, ignore_index=True)
    
    # 2. Filter & Prep
    # We use the h=13 (July vs Oct) bandwidth and Post-AI outcome
    h = 13
    outcome = "post_ai_downloads_alltime"
    
    # Apply Donut and Bandwidth
    df = df[~df["dist_to_cutoff"].isin(DONUT_WEEKS)]
    df = df[(df["dist_to_cutoff"] >= -h) & (df["dist_to_cutoff"] <= h)].copy()
    
    # Baseline filter (Min 10 downloads in first 52 weeks)
    df = df[df["total_downloads_52wk"] >= 10].copy()
    
    # Log Transformation
    df["log_y"] = np.log1p(df[outcome])
    df["x"] = df["dist_to_cutoff"]
    df["treated"] = (df["x"] >= 0).astype(int) # October cohort
    
    # Triangular Weights: w = 1 - |x/h|
    df["weight"] = 1 - (np.abs(df["x"]) / h)
    df = df[df["weight"] > 0]
    
    # 3. Diff-in-RDD Specification
    # Specification: LogY ~ treated*is_2021 + x*treated*is_2021
    # This allows for separate slopes on each side of the cutoff for each group
    formula = "log_y ~ treated * is_2021 + x * treated * is_2021"
    
    print(f"Estimating Diff-in-RDD (2018-2020 Pooled Placebos vs 2021 Main)...")
    print(f"Outcome: log(1 + {outcome})")
    
    # Cluster by week-dist-to-cutoff for robust inference
    df['cluster_idx'] = df["dist_to_cutoff"].astype('category').cat.codes
    
    try:
        model = smf.wls(formula, data=df, weights=df["weight"]).fit(
            cov_type='cluster', 
            cov_kwds={'groups': df["cluster_idx"]}
        )
        
        # The key coefficient is the interaction between 'treated' and 'is_2021'
        # It represents the excess jump in 2021 relative to the placebo years
        coef = model.params["treated:is_2021"]
        se = model.bse["treated:is_2021"]
        pval = model.pvalues["treated:is_2021"]
        
        print("\n=========================================")
        print("      DIFF-IN-RDD ESTIMATION RESULTS     ")
        print("=========================================\n")
        print(f"Excess Jump (2021 vs Placebos): {coef:.4f}")
        print(f"Standard Error:                 {se:.4f}")
        print(f"P-value:                        {pval:.4f}")
        print(f"Total Observations (N):         {int(model.nobs)}")
        
        # Save summary
        with open(RESULTS_DIR / "diff_in_rdd_detailed_report.txt", "w") as f:
            f.write(model.summary().as_text())
        
        # Also save as CSV for later visualization
        results_summary = pd.DataFrame([{
            "Outcome": outcome,
            "Excess_Jump": coef,
            "Std_Err": se,
            "P_value": pval,
            "N": int(model.nobs)
        }])
        results_summary.to_csv(RESULTS_DIR / "diff_in_rdd_final.csv", index=False)
        
    except Exception as e:
        print(f"Error in Diff-in-RDD estimation: {e}")

if __name__ == "__main__":
    main()
