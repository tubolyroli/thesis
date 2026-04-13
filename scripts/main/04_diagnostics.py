import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS, MIN_SUCCESS_LOW
from utils import setup_plotting_style, check_monday_alignment, run_rdrobust_est

def main():
    setup_plotting_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found. Run scripts 01-03 first.")
        return

    df = pd.read_csv(MAIN_ANALYSIS_DATA, parse_dates=["release_week"])
    
    print("=========================================")
    print("      THESIS DIAGNOSTICS REPORT          ")
    print("=========================================\n")
    
    # Sample counts
    print("--- 1. Sample Size & Matching Coverage ---")
    total_obs = len(df)
    print(f"Total libraries in window: {total_obs:,}")
    if "matched_to_github" in df.columns:
        matched = int(df["matched_to_github"].sum())
        print(f"Matched to GitHub:   {matched:,} ({matched/total_obs:.1%})")
    print("")

    # Date alignment
    print("--- 2. Date Alignment Check ---")
    try:
        check_monday_alignment(df, "release_week")
        print("✓ All release weeks are correctly aligned to Monday.\n")
    except ValueError as e:
        print(f"⚠ WARNING: {e}\n")

    # Running variable
    print("--- 3. Running Variable (dist_to_cutoff) ---")
    print(f"Min: {df['dist_to_cutoff'].min():.0f} weeks")
    print(f"Max: {df['dist_to_cutoff'].max():.0f} weeks")
    print(f"Donut share: {df['in_donut'].mean():.1%}\n")

    # Outcomes
    print("--- 4. Outcome Distributions (Full Sample for Downloads, Conditional on GitHub Match for Imports) ---")
    outcomes = ["total_downloads_52wk"]
    if "avg_ai_score_52wk" in df.columns:
        outcomes.append("avg_ai_score_52wk")
        
    stats_dl = df[outcomes].describe().transpose()
    
    # Imports only for matched
    df_matched = df[df["matched_to_github"] == 1]
    stats_imp = df_matched[["cum_imports_52wk"]].describe().transpose()
    stats_imp.index = ["cum_imports_52wk (Cond. on Match)"]
    
    stats = pd.concat([stats_dl, stats_imp])
    print(stats.round(3).to_string())
    print("")

    # Naive comparison
    print("--- 5. Pre/Post Cutoff Naive Comparison (Imports Conditional on Match) ---")
    df_no_donut = df[df["in_donut"] == 0]
    comp_dl = df_no_donut.groupby("is_pre_cutoff")[outcomes].mean()
    
    df_matched_no_donut = df_no_donut[df_no_donut["matched_to_github"] == 1]
    comp_imp = df_matched_no_donut.groupby("is_pre_cutoff")[["cum_imports_52wk"]].mean()
    comp_imp.columns = ["cum_imports_52wk (Cond. on Match)"]
    
    comparison = pd.concat([comp_dl, comp_imp], axis=1).round(2)
    comparison.index = ["Post-Cutoff (0)", "Pre-Cutoff (1)"]
    print(comparison.to_string())

    # Figures
    print("\n--- Generating Figures ---")
    
    # Density plot
    plt.figure()
    counts = df.groupby("dist_to_cutoff").size()
    plt.bar(counts.index, counts.values, color="steelblue", edgecolor="black", alpha=0.8)
    plt.axvline(0, color="red", linestyle="--", linewidth=2, label="Cutoff")
    plt.title("Density of Python Library Releases")
    plt.xlabel("Weeks from Cutoff")
    plt.ylabel("Number of Libraries")
    plt.savefig(FIGURES_DIR / "density_dist_to_cutoff.png", dpi=300)
    plt.close()

    # McCrary-style density test (local linear with separate slopes each side)
    print("\n--- 6. McCrary-Style Density Test ---")
    density_results = []
    for h_test in [13, 26]:
        bin_counts = df.groupby("dist_to_cutoff").size().reset_index(name="count")
        bin_counts = bin_counts[(bin_counts["dist_to_cutoff"] >= -h_test) &
                                (bin_counts["dist_to_cutoff"] <= h_test)].copy()
        bin_counts["log_count"] = np.log(bin_counts["count"])
        bin_counts["post"] = (bin_counts["dist_to_cutoff"] >= 0).astype(int)
        bin_counts["x_post"] = bin_counts["dist_to_cutoff"] * bin_counts["post"]
        X = sm.add_constant(bin_counts[["dist_to_cutoff", "post", "x_post"]])
        model = sm.OLS(bin_counts["log_count"], X).fit()
        theta = model.params["post"]
        se = model.bse["post"]
        pval = model.pvalues["post"]
        print(f"  h={h_test}: theta={theta:+.3f}, SE={se:.3f}, p={pval:.3f}")
        density_results.append({"bandwidth": h_test, "theta": theta, "se": se, "p_value": pval})
    pd.DataFrame(density_results).to_csv(RESULTS_DIR / "density_test_results.csv", index=False)
    print(f"  Saved to {RESULTS_DIR / 'density_test_results.csv'}")

    # Pre-AI Covariate Balance: Pr(Successful) RDD
    print("\n--- 7. Pre-AI Covariate Balance RDD ---")
    df["is_successful"] = (df["cum_downloads_26wk"] >= MIN_SUCCESS_LOW).astype(int)
    cov_result = run_rdrobust_est(
        df, "is_successful", h=26, donut_weeks=DONUT_WEEKS,
        label="Covariate Balance: Pr(Successful)"
    )
    cov_df = pd.DataFrame([cov_result])
    cov_df.to_csv(RESULTS_DIR / "covariate_balance_rdd.csv", index=False)
    print(f"  Estimate: {cov_result.get('Estimate', 'N/A')}")
    print(f"  P-value:  {cov_result.get('P-value', 'N/A')}")
    print(f"  N:        {cov_result.get('N', 'N/A')}")
    print(f"  Saved to {RESULTS_DIR / 'covariate_balance_rdd.csv'}")

    # Outcome Dist
    plt.figure()
    sns.histplot(np.log1p(df["cum_imports_52wk"]), bins=50, kde=False, color="purple")
    plt.title("Distribution of 52-Week GitHub Imports (Log Scale)")
    plt.xlabel("Log(1 + Imports)")
    plt.savefig(FIGURES_DIR / "outcome_dist_log_imports.png", dpi=300)
    plt.close()

    # Binscatter
    plt.figure()
    df["log_imports_52wk"] = np.log1p(df["cum_imports_52wk"])
    binscatter = df.groupby("dist_to_cutoff")["log_imports_52wk"].mean().reset_index()
    sns.scatterplot(data=binscatter, x="dist_to_cutoff", y="log_imports_52wk", color="darkblue")
    plt.axvline(0, color="red", linestyle="--", label="Cutoff")
    plt.title("Binned Scatterplot: 52-Week Imports by Release Date")
    plt.xlabel("Weeks from Cutoff")
    plt.ylabel("Mean Log(1 + Imports)")
    plt.savefig(FIGURES_DIR / "binscatter_log_imports.png", dpi=300)
    plt.close()
    
    print(f"Figures saved to {FIGURES_DIR}")

if __name__ == "__main__":
    main()
