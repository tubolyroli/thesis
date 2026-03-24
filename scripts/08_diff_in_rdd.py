import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import FINAL_DIR, RESULTS_DIR, DONUT_WEEKS, DEFAULT_BW, MIN_DOWNLOADS_FILTER, MIN_SUCCESS_LOW, MIN_SUCCESS_HIGH

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
        df_main["cutoff_year"] = 2021
        dfs.append(df_main)
    
    # Load Placebos
    for p in placebos:
        p_path = FINAL_DIR / f"analysis_{p}.csv"
        if p_path.exists():
            df_p = pd.read_csv(p_path)
            df_p["is_2021"] = 0
            # Extract year from filename (e.g., 'Placebo_2018' -> 2018)
            df_p["cutoff_year"] = int(p.split("_")[1])
            dfs.append(df_p)
            
    if not dfs:
        print("Required analysis files for Diff-in-RDD not found.")
        return

    # Pool all years
    df = pd.concat(dfs, ignore_index=True)
    
    # 2. Filter & Prep
    # We test two windows: 
    # 1. total_downloads_52wk (Mostly pre-ChatGPT for 2021 cohort)
    # 2. post_ai_downloads_alltime (Post-Nov 2022 only - Activation Window)
    h = DEFAULT_BW
    outcomes = ["total_downloads_52wk", "post_ai_downloads_alltime"]
    
    # Apply Donut and Bandwidth
    df = df[~df["dist_to_cutoff"].isin(DONUT_WEEKS)]
    df = df[(df["dist_to_cutoff"] >= -h) & (df["dist_to_cutoff"] <= h)].copy()
    
    # Baseline filter (Min 10 downloads in first 52 weeks)
    df_min10 = df[df["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
    
    # Subsample: "Successful" Libraries (Pre-GPT Winners)
    # Using 26-week horizon as suggested by supervisor
    df_success_low = df[df["cum_downloads_26wk"] >= MIN_SUCCESS_LOW].copy()
    df_success_high = df[df["cum_downloads_26wk"] >= MIN_SUCCESS_HIGH].copy()

    results = []
    tiers = [
        (df_min10, "Broad"),
        (df_success_low, f"Successful (min{MIN_SUCCESS_LOW}@26w)"),
        (df_success_high, f"Superstar (min{MIN_SUCCESS_HIGH}@26w)")
    ]

    for df_tier, tier_label in tiers:
        for outcome in outcomes:
            print(f"Estimating Diff-in-RDD for tier: {tier_label}, outcome: {outcome} (N={len(df_tier)})...")
            if len(df_tier) < 50:
                print(f"  Skipping {tier_label} due to insufficient data.")
                continue
                
            # Log Transformation
            df_tier["log_y"] = np.log1p(df_tier[outcome])
            df_tier["x"] = df_tier["dist_to_cutoff"]
            df_tier["treated"] = (df_tier["x"] >= 0).astype(int) # October cohort
            
            # Triangular Weights: w = 1 - |x/h|
            df_tier["weight"] = 1 - (np.abs(df_tier["x"]) / h)
            df_tier = df_tier[df_tier["weight"] > 0]
            
            # Specification: Fully Interacted Diff-in-RDD
            # Y ~ treated * is_2021 + x * treated * is_2021
            # The coefficient on 'treated:is_2021' is the Diff-in-RDD (Excess Jump)
            
            # Rigorous Clustering: year_by_week (not just week)
            # Fix: use actual year × week = 4 years × 18 weeks = 72 clusters
            df_tier['cluster_idx'] = df_tier["cutoff_year"].astype(str) + "_" + df_tier["dist_to_cutoff"].astype(str)
            
            try:
                # We use a linear probability model/WLS with triangular weights
                model = smf.wls("log_y ~ treated * is_2021 + x * treated * is_2021", 
                                data=df_tier, weights=df_tier["weight"]).fit(
                    cov_type='cluster', 
                    cov_kwds={'groups': df_tier["cluster_idx"]}
                )
                
                coef = model.params["treated:is_2021"]
                se = model.bse["treated:is_2021"]
                pval = model.pvalues["treated:is_2021"]
                
                results.append({
                    "Tier": tier_label,
                    "Outcome": outcome,
                    "Excess_Jump": coef,
                    "Std_Err": se,
                    "P_value": pval,
                    "N": int(model.nobs)
                })
            except Exception as e:
                print(f"  Error in {tier_label} Diff-in-RDD estimation: {e}")

    # Compile and Save Results
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "diff_in_rdd_tiers.csv", index=False)
    
    print("\n=========================================")
    print("      DIFF-IN-RDD ESTIMATION RESULTS     ")
    print("=========================================\n")
    print(results_df[["Tier", "Outcome", "Excess_Jump", "Std_Err", "P_value", "N"]].round(4).to_string(index=False))
    
    # Save the Broad result for final summary
    broad_res = results_df[results_df["Tier"] == "Broad"]
    if not broad_res.empty:
        broad_res.to_csv(RESULTS_DIR / "diff_in_rdd_final.csv", index=False)

if __name__ == "__main__":
    main()
