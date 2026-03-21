import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
from scipy.stats import norm
from config import MAIN_ANALYSIS_DATA, RESULTS_DIR, FIGURES_DIR, DONUT_WEEKS
from utils import run_local_linear_rdd, setup_plotting_style

def plot_rdd_comparison(df, outcome_col, h=26, donut_weeks=None, group_col=None, labels=None):
    """
    Creates a side-by-side RDD binscatter plot for comparison.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    
    for i, (group_val, label) in enumerate(labels.items()):
        sub = df[df[group_col] == group_val].copy()
        
        # Apply filters
        if donut_weeks:
            sub = sub[~sub["dist_to_cutoff"].isin(donut_weeks)]
        sub = sub[(sub["dist_to_cutoff"] >= -h) & (sub["dist_to_cutoff"] <= h)].copy()
        
        # Log outcome
        sub["y"] = np.log1p(sub[outcome_col])
        sub["x"] = sub["dist_to_cutoff"]
        
        # Binscatter
        sns.regplot(x="x", y="y", data=sub[sub["x"] < 0], x_bins=15, ax=axes[i], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        sns.regplot(x="x", y="y", data=sub[sub["x"] >= 0], x_bins=15, ax=axes[i], scatter_kws={'alpha':0.5}, line_kws={'color':'blue'})
        
        axes[i].axvline(0, color="black", linestyle="--", alpha=0.5)
        axes[i].set_title(f"Mechanism Split: {label} (N={len(sub)})")
        axes[i].set_xlabel("Weeks since Cutoff")
        axes[i].set_ylabel(f"log(1 + {outcome_col})")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"mechanism_split_{outcome_col}.png")
    print(f"Saved mechanism plot to {FIGURES_DIR / f'mechanism_split_{outcome_col}.png'}")

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()

    if not MAIN_ANALYSIS_DATA.exists():
        print(f"Error: {MAIN_ANALYSIS_DATA} not found.")
        return

    df = pd.read_csv(MAIN_ANALYSIS_DATA)
    
    # 1. Define Mechanism Split: AI vs Human
    # NOTE: avg_ai_score_52wk is measured post-release and thus potentially 
    # post-treatment. This analysis is EXPLORATORY and should be treated as 
    # descriptive heterogeneity rather than causal moderation.
    print("\n--- APPENDIX: Exploratory Mechanism Split ---")
    print("WARNING: Splitting on post-treatment AI scores may introduce selection bias.\n")
    
    df_ai = df.dropna(subset=["avg_ai_score_52wk"]).copy()
    
    if df_ai.empty:
        print("Warning: No AI score data available for mechanism test.")
        return

    median_ai = df_ai["avg_ai_score_52wk"].median()
    df_ai["high_ai"] = (df_ai["avg_ai_score_52wk"] > median_ai).astype(int)
    
    print(f"Running mechanism-driven split-sample RDD...")
    print(f"Sample: Libraries with AI-scored GitHub usage (N={len(df_ai)})")
    print(f"Median Split at AI Score: {median_ai:.3f}")

    results = []
    labels = {1: "High AI Exposure", 0: "Low AI Exposure"}
    
    # Outcomes: downloads and imports
    outcomes = ["total_downloads_52wk", "cum_imports_52wk"]
    
    for out in outcomes:
        for group_val, label in labels.items():
            sub = df_ai[df_ai["high_ai"] == group_val]
            # Primary: WLS with Week-Clustered standard errors (most robust for time-based RDD)
            res = run_local_linear_rdd(sub, out, h=26, donut_weeks=DONUT_WEEKS, label=f"Appendix: {label}", cluster_col="dist_to_cutoff")
            results.append(res)
        
        # Visualization for each outcome
        plot_rdd_comparison(df_ai, out, h=26, donut_weeks=DONUT_WEEKS, group_col="high_ai", labels=labels)

    # Compile and Save
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "mechanism_split_results.csv", index=False)

    # Calculate Rigorous Difference-in-Discontinuities (Interacted Model)
    # Model: log_y ~ treated * high_ai + x * treated * high_ai
    # The coefficient on 'treated:high_ai' is the formal test of mechanism moderation.
    print("\n--- Formal Mechanism Moderation Test (Interacted Model) ---")
    
    diff_results = []
    for out in outcomes:
        df_ai["log_y"] = np.log1p(df_ai[out])
        df_ai["x"] = df_ai["dist_to_cutoff"]
        df_ai["treated"] = (df_ai["x"] >= 0).astype(int)
        
        # Triangular Weights
        h_interact = 26
        df_ai["weight"] = 1 - (np.abs(df_ai["x"]) / h_interact)
        sub_interact = df_ai[df_ai["weight"] > 0].copy()
        
        # Interaction Model with clustered SEs
        sub_interact['cluster_id'] = sub_interact["dist_to_cutoff"].astype('category').cat.codes
        model = smf.wls("log_y ~ treated * high_ai + x * treated * high_ai", 
                        data=sub_interact, weights=sub_interact["weight"]).fit(
            cov_type='cluster', 
            cov_kwds={'groups': sub_interact["cluster_id"]}
        )
        
        coef_diff = model.params["treated:high_ai"]
        se_diff = model.bse["treated:high_ai"]
        pval_diff = model.pvalues["treated:high_ai"]
        
        diff_results.append({
            "Outcome": out,
            "Diff_in_Discontinuity": coef_diff,
            "Std_Err": se_diff,
            "P-value": pval_diff,
            "N": int(model.nobs)
        })

    print("\n=========================================")
    print("      MECHANISM MODERATION RESULTS       ")
    print("=========================================\n")
    diff_df = pd.DataFrame(diff_results)
    print(diff_df.round(4).to_string(index=False))
    
    # Save the interaction results to CSV for reproducibility
    interaction_out_path = RESULTS_DIR / "mechanism_interaction_results.csv"
    diff_df.to_csv(interaction_out_path, index=False)
    print(f"\nSaved formal interaction results to {interaction_out_path}")

if __name__ == "__main__":
    main()
