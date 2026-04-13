import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
            df_p["cutoff_year"] = int(p.split("_")[1])
            dfs.append(df_p)

    if not dfs:
        print("Required analysis files for Diff-in-RDD not found.")
        return

    # Pool all years
    df = pd.concat(dfs, ignore_index=True)

    # 2. Filter & Prep
    h = DEFAULT_BW
    outcomes = ["total_downloads_52wk", "post_ai_downloads_alltime"]

    # Apply Donut and Bandwidth
    df = df[~df["dist_to_cutoff"].isin(DONUT_WEEKS)]
    df = df[(df["dist_to_cutoff"] >= -h) & (df["dist_to_cutoff"] <= h)].copy()

    # Tier definitions
    df_min10 = df[df["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
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
            for adjusted in [False, True]:
                # Skip baseline adjustment when outcome IS the baseline (circular)
                if adjusted and outcome == "total_downloads_52wk":
                    continue

                print(f"Estimating Diff-in-RDD: tier={tier_label}, outcome={outcome}, adjusted={adjusted} (N={len(df_tier)})...")
                if len(df_tier) < 50:
                    print(f"  Skipping {tier_label} due to insufficient data.")
                    results.append({
                        "Tier": tier_label,
                        "Outcome": outcome,
                        "Excess_Jump": np.nan,
                        "Std_Err": np.nan,
                        "P_value": np.nan,
                        "N": int(len(df_tier)),
                        "Baseline_Adjusted": adjusted,
                        "Note": "skipped: N<50"
                    })
                    continue

                df_work = df_tier.copy()
                df_work["log_y"] = np.log1p(df_work[outcome])
                df_work["x"] = df_work["dist_to_cutoff"]
                df_work["treated"] = (df_work["x"] >= 0).astype(int)

                # Triangular Weights
                df_work["weight"] = 1 - (np.abs(df_work["x"]) / h)
                df_work = df_work[df_work["weight"] > 0]

                # Clustering: year-by-week
                df_work['cluster_idx'] = df_work["cutoff_year"].astype(str) + "_" + df_work["dist_to_cutoff"].astype(str)

                # Build formula
                if adjusted:
                    df_work["log_baseline"] = np.log1p(df_work["total_downloads_52wk"])
                    formula = "log_y ~ log_baseline + treated * is_2021 + x * treated * is_2021"
                else:
                    formula = "log_y ~ treated * is_2021 + x * treated * is_2021"

                try:
                    model = smf.wls(formula, data=df_work, weights=df_work["weight"]).fit(
                        cov_type='cluster',
                        cov_kwds={'groups': df_work["cluster_idx"]}
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
                        "N": int(model.nobs),
                        "Baseline_Adjusted": adjusted
                    })
                except Exception as e:
                    print(f"  Error in {tier_label} Diff-in-RDD estimation: {e}")

    # Compile and Save Results
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "diff_in_rdd_tiers.csv", index=False)

    print("\n=========================================")
    print("      DIFF-IN-RDD ESTIMATION RESULTS     ")
    print("=========================================\n")
    print(results_df[["Tier", "Outcome", "Excess_Jump", "Std_Err", "P_value", "N", "Baseline_Adjusted"]].round(4).to_string(index=False))

    # Save the Broad result for final summary
    broad_res = results_df[results_df["Tier"] == "Broad"]
    if not broad_res.empty:
        broad_res.to_csv(RESULTS_DIR / "diff_in_rdd_final.csv", index=False)

    # --- DV Summary Statistics (for thesis table notes) ---
    # Compute mean and SD of log(1+Y) per tier/outcome for 2021 cohort only, within bandwidth
    dv_stats = []
    for df_tier, tier_label in tiers:
        for outcome in outcomes:
            df_2021 = df_tier[df_tier["is_2021"] == 1].copy()
            if len(df_2021) == 0:
                continue
            log_y = np.log1p(df_2021[outcome].dropna())
            dv_stats.append({
                "Tier": tier_label,
                "Outcome": outcome,
                "DV_Mean": log_y.mean(),
                "DV_SD": log_y.std(),
                "DV_N": len(log_y)
            })

    dv_stats_df = pd.DataFrame(dv_stats)
    dv_stats_df.to_csv(RESULTS_DIR / "diff_in_rdd_dv_stats.csv", index=False)

    print("\n=========================================")
    print("      DV SUMMARY STATISTICS (2021)       ")
    print("=========================================\n")
    print(dv_stats_df.round(4).to_string(index=False))

    # --- GitHub-Matched Subsample Diff-in-RDD ---
    print("\n=========================================")
    print("   GITHUB-MATCHED DIFF-IN-RDD RESULTS    ")
    print("=========================================\n")

    df_gh = df[df["matched_to_github"] == 1].copy()

    gh_outcomes = [
        ("cum_imports_52wk", "GitHub"),
        ("post_ai_imports_alltime", "GitHub"),
        ("cum_imports_alltime", "GitHub"),
        ("total_downloads_52wk", "PyPI"),
        ("post_ai_downloads_alltime", "PyPI"),
    ]

    # Tier definitions on GitHub-matched subsample
    df_gh_min10 = df_gh[df_gh["total_downloads_52wk"] >= MIN_DOWNLOADS_FILTER].copy()
    df_gh_success_low = df_gh[df_gh["cum_downloads_26wk"] >= MIN_SUCCESS_LOW].copy()
    df_gh_success_high = df_gh[df_gh["cum_downloads_26wk"] >= MIN_SUCCESS_HIGH].copy()

    gh_tiers = [
        (df_gh_min10, "Broad"),
        (df_gh_success_low, "Successful"),
        (df_gh_success_high, "Superstar"),
    ]

    gh_results = []
    for df_gh_tier, tier_label in gh_tiers:
        for outcome, outcome_type in gh_outcomes:
            if outcome not in df_gh_tier.columns:
                continue
            for adjusted in [False, True]:
                # Skip circular baseline adjustment
                if adjusted and outcome == "total_downloads_52wk":
                    continue
                if adjusted and outcome == "cum_imports_52wk":
                    continue

                print(f"GitHub Diff-in-RDD: tier={tier_label}, outcome={outcome}, type={outcome_type}, adjusted={adjusted} (N={len(df_gh_tier)})...")
                if len(df_gh_tier) < 50:
                    print(f"  Skipping {tier_label} due to insufficient data.")
                    gh_results.append({
                        "Tier": tier_label, "Outcome": outcome, "Type": outcome_type,
                        "Excess_Jump": np.nan, "Std_Err": np.nan, "P_value": np.nan,
                        "N": int(len(df_gh_tier)), "Adjusted": adjusted
                    })
                    continue

                df_work = df_gh_tier.copy()
                df_work["log_y"] = np.log1p(df_work[outcome])
                df_work["x"] = df_work["dist_to_cutoff"]
                df_work["treated"] = (df_work["x"] >= 0).astype(int)

                # Triangular Weights
                df_work["weight"] = 1 - (np.abs(df_work["x"]) / h)
                df_work = df_work[df_work["weight"] > 0]

                # Clustering: year-by-week
                df_work['cluster_idx'] = df_work["cutoff_year"].astype(str) + "_" + df_work["dist_to_cutoff"].astype(str)

                # Build formula
                if adjusted:
                    df_work["log_baseline"] = np.log1p(df_work["total_downloads_52wk"])
                    formula = "log_y ~ log_baseline + treated * is_2021 + x * treated * is_2021"
                else:
                    formula = "log_y ~ treated * is_2021 + x * treated * is_2021"

                try:
                    model = smf.wls(formula, data=df_work, weights=df_work["weight"]).fit(
                        cov_type='cluster',
                        cov_kwds={'groups': df_work["cluster_idx"]}
                    )

                    coef = model.params["treated:is_2021"]
                    se = model.bse["treated:is_2021"]
                    pval = model.pvalues["treated:is_2021"]

                    gh_results.append({
                        "Tier": tier_label, "Outcome": outcome, "Type": outcome_type,
                        "Excess_Jump": coef, "Std_Err": se, "P_value": pval,
                        "N": int(model.nobs), "Adjusted": adjusted
                    })
                except Exception as e:
                    print(f"  Error in {tier_label} GitHub Diff-in-RDD: {e}")

    gh_results_df = pd.DataFrame(gh_results)
    gh_results_df.to_csv(RESULTS_DIR / "github_diff_in_rdd.csv", index=False)

    print("\n--- GitHub Diff-in-RDD Results ---")
    print(gh_results_df[["Tier", "Outcome", "Type", "Excess_Jump", "Std_Err", "P_value", "N", "Adjusted"]].round(4).to_string(index=False))

if __name__ == "__main__":
    main()
