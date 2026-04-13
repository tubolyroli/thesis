import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

    main_path = FINAL_DIR / f"analysis_{main_cutoff}.csv"
    if main_path.exists():
        df_main = pd.read_csv(main_path)
        df_main["is_2021"] = 1
        df_main["cutoff_year"] = 2021
        dfs.append(df_main)

    for p in placebos:
        p_path = FINAL_DIR / f"analysis_{p}.csv"
        if p_path.exists():
            df_p = pd.read_csv(p_path)
            df_p["is_2021"] = 0
            df_p["cutoff_year"] = int(p.split("_")[1])
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
    bandwidths = [10, 13, 15, 18, 26]
    results = []

    print(f"Running Diff-in-RDD Bandwidth Sensitivity for Successful Tier...")

    for h in bandwidths:
        for adjusted in [False, True]:
            # Filter by BW and exclude Donut
            df_h = df_success[~df_success["dist_to_cutoff"].isin(DONUT_WEEKS)].copy()
            df_h = df_h[(df_h["dist_to_cutoff"] >= -h) & (df_h["dist_to_cutoff"] <= h)].copy()

            if len(df_h) < 100:
                print(f"  Skipping h={h}, adj={adjusted} due to small N={len(df_h)}")
                continue

            # Log outcome
            df_h["log_y"] = np.log1p(df_h[outcome])
            df_h["x"] = df_h["dist_to_cutoff"]
            df_h["treated"] = (df_h["x"] >= 0).astype(int)

            # Triangular Weights
            df_h["weight"] = 1 - (np.abs(df_h["x"]) / h)
            df_h = df_h[df_h["weight"] > 0]

            # Clustering: year-by-week
            df_h['cluster_idx'] = df_h["cutoff_year"].astype(str) + "_" + df_h["dist_to_cutoff"].astype(str)

            # Build formula
            if adjusted:
                df_h["log_baseline"] = np.log1p(df_h["total_downloads_52wk"])
                formula = "log_y ~ log_baseline + treated * is_2021 + x * treated * is_2021"
            else:
                formula = "log_y ~ treated * is_2021 + x * treated * is_2021"

            try:
                model = smf.wls(formula, data=df_h, weights=df_h["weight"]).fit(
                    cov_type='cluster',
                    cov_kwds={'groups': df_h["cluster_idx"]}
                )

                coef = model.params["treated:is_2021"]
                se = model.bse["treated:is_2021"]
                pval = model.pvalues["treated:is_2021"]

                if np.isnan(se) or np.abs(coef) > 500:
                    print(f"  h={h}, adj={adjusted}: Skipping due to numerical instability.")
                    continue

                results.append({
                    "BW": h,
                    "Excess_Jump": coef,
                    "Std_Err": se,
                    "P_value": pval,
                    "N": int(model.nobs),
                    "Baseline_Adjusted": adjusted
                })
                print(f"  h={h}, adj={adjusted}: Est={coef:.4f}, p={pval:.4f}, N={model.nobs}")
            except Exception as e:
                print(f"  Error at h={h}, adj={adjusted}: {e}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "sensitivity_diff_in_rdd_bandwidth.csv", index=False)

    # 4. Plotting (adjusted as primary, unadjusted as comparison)
    fig, ax = plt.subplots(figsize=(10, 6))

    for adj_val, color, lbl in [(True, 'darkred', 'Baseline-adjusted'), (False, 'steelblue', 'Unadjusted')]:
        sub = results_df[results_df["Baseline_Adjusted"] == adj_val]
        if not sub.empty:
            offset = 0.15 if adj_val else -0.15
            ax.errorbar(sub["BW"] + offset, sub["Excess_Jump"],
                        yerr=1.96 * sub["Std_Err"],
                        fmt='o-', color=color, capsize=5, linewidth=2, label=lbl)

    ax.axhline(0, color='black', linestyle='--', alpha=0.5)
    ax.set_title(f"Bandwidth Sensitivity: Diff-in-RDD Excess Jump\n(Successful tier, min {MIN_SUCCESS_LOW} @ 26w)", fontweight='bold')
    ax.set_xlabel("Bandwidth (Weeks from Cutoff)")
    ax.set_ylabel("Diff-in-RDD Estimate")
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sensitivity_diff_in_rdd_bandwidth.png", dpi=300)
    print(f"Saved sensitivity plot to {FIGURES_DIR / 'sensitivity_diff_in_rdd_bandwidth.png'}")

if __name__ == "__main__":
    main()
