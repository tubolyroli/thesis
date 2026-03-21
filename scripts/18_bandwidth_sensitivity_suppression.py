import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from config import FINAL_DIR, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS, MIN_SUCCESS_LOW
from utils import setup_plotting_style

def main():
    setup_plotting_style()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load 2018-2020 (Placebos) and 2021 (Main)
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
        print("Required analysis files not found.")
        return

    df_full = pd.concat(dfs, ignore_index=True)
    
    # 2. Filter for "Successful" Libraries (min 500 at 26 weeks)
    df_success = df_full[df_full["cum_downloads_26wk"] >= MIN_SUCCESS_LOW].copy()
    print(f"Total Successful Sample: {len(df_success)}")

    # 3. Parameters
    outcome = "post_ai_downloads_alltime"
    bandwidths = [10, 13, 15, 18, 26] # weeks (h=8 removed as unidentified)
    results = []

    print(f"Running Diff-in-RDD Bandwidth Sensitivity for Successful Tier...")
    
    for h in bandwidths:
        # Filter by BW and exclude Donut
        df_h = df_success[~df_success["dist_to_cutoff"].isin(DONUT_WEEKS)].copy()
        df_h = df_h[(df_h["dist_to_cutoff"] >= -h) & (df_h["dist_to_cutoff"] <= h)].copy()
        
        if len(df_h) < 100:
            print(f"  Skipping h={h} due to small N={len(df_h)}")
            continue
            
        # Log outcome
        df_h["log_y"] = np.log1p(df_h[outcome])
        df_h["x"] = df_h["dist_to_cutoff"]
        df_h["treated"] = (df_h["x"] >= 0).astype(int)
        
        # Triangular Weights: w = 1 - |x/h|
        df_h["weight"] = 1 - (np.abs(df_h["x"]) / h)
        df_h = df_h[df_h["weight"] > 0]
        
        # Rigorous Clustering: year-by-week
        df_h['cluster_idx'] = df_h["is_2021"].astype(str) + "_" + df_h["dist_to_cutoff"].astype(str)
        
        try:
            model = smf.wls("log_y ~ treated * is_2021 + x * treated * is_2021", 
                            data=df_h, weights=df_h["weight"]).fit(
                cov_type='cluster', 
                cov_kwds={'groups': df_h["cluster_idx"]}
            )
            
            coef = model.params["treated:is_2021"]
            se = model.bse["treated:is_2021"]
            pval = model.pvalues["treated:is_2021"]
            
            # Stability Check: Skip unidentified or exploding results
            if np.isnan(se) or np.abs(coef) > 500:
                print(f"  h={h}: Skipping due to numerical instability (singular matrix).")
                continue

            results.append({
                "BW": h,
                "Excess_Jump": coef,
                "Std_Err": se,
                "P_value": pval,
                "N": int(model.nobs)
            })
            print(f"  h={h}: Est={coef:.4f}, p={pval:.4f}, N={model.nobs}")
        except Exception as e:
            print(f"  Error at h={h}: {e}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "sensitivity_diff_in_rdd_bandwidth.csv", index=False)
    
    # 4. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(results_df["BW"], results_df["Excess_Jump"], 
                yerr=1.96 * results_df["Std_Err"], 
                fmt='o-', color='darkred', capsize=5, linewidth=2, label="Excess Jump (2021 vs Placebos)")
    
    ax.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax.set_title(f"Bandwidth Sensitivity: The 'Suppression' Excess Jump\n(Subsample: Successful Libraries, min {MIN_SUCCESS_LOW} @ 26w)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Bandwidth (Weeks from Cutoff)", fontsize=12)
    ax.set_ylabel("Diff-in-RDD Estimate (Log Scale)", fontsize=12)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sensitivity_diff_in_rdd_bandwidth.png", dpi=300)
    print(f"Saved sensitivity plot to {FIGURES_DIR / 'sensitivity_diff_in_rdd_bandwidth.png'}")

if __name__ == "__main__":
    main()
