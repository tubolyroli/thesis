import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import FINAL_DIR, RESULTS_ROBUSTNESS, FIG_ROBUSTNESS, DONUT_WEEKS
from utils import run_local_linear_rdd, run_quantile_rdd, setup_plotting_style

def main():
    RESULTS_ROBUSTNESS.mkdir(parents=True, exist_ok=True)
    FIG_ROBUSTNESS.mkdir(parents=True, exist_ok=True)
    setup_plotting_style()
    
    # 1. Load and Pool Placebo Cutoffs (2018, 2019, 2020)
    placebos = ["Placebo_2018", "Placebo_2019", "Placebo_2020"]
    pooled_list = []
    
    for p in placebos:
        path = FINAL_DIR / f"analysis_{p}.csv"
        if path.exists():
            tmp = pd.read_csv(path)
            tmp["cutoff_year"] = p
            tmp["is_main_2021"] = 0
            pooled_list.append(tmp)
            
    # Add 2021 for comparison
    main_path = FINAL_DIR / "analysis_Main_2021.csv"
    if main_path.exists():
        tmp_main = pd.read_csv(main_path)
        tmp_main["cutoff_year"] = "Main_2021"
        tmp_main["is_main_2021"] = 1
        pooled_list.append(tmp_main)
        
    df_stack = pd.concat(pooled_list, ignore_index=True)
    df_stack_min10 = df_stack[df_stack["total_downloads_52wk"] >= 10].copy()
    
    # 2. Estimate Average Placebo Jump (Log Mean)
    print("Estimating Average Placebo Jump (2018-2020)...")
    df_placebo_pool = df_stack_min10[df_stack_min10["is_main_2021"] == 0].copy()
    res_placebo_mean = run_local_linear_rdd(df_placebo_pool, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label="Stacked Placebos (Mean)", cluster_col="dist_to_cutoff")
    
    # 3. Estimate Average Placebo Jump (Median)
    print("Estimating Average Placebo Jump (Median)...")
    res_placebo_median = run_quantile_rdd(df_placebo_pool, "total_downloads_52wk", q=0.5, h=26, donut_weeks=DONUT_WEEKS, label="Stacked Placebos (Median)")
    
    # 4. Compare with 2021
    print("Estimating 2021 Main Jump for comparison...")
    df_main = df_stack_min10[df_stack_min10["is_main_2021"] == 1].copy()
    res_main_mean = run_local_linear_rdd(df_main, "total_downloads_52wk", h=26, donut_weeks=DONUT_WEEKS, label="Main 2021 (Mean)", cluster_col="dist_to_cutoff")
    res_main_median = run_quantile_rdd(df_main, "total_downloads_52wk", q=0.5, h=26, donut_weeks=DONUT_WEEKS, label="Main 2021 (Median)")
    
    # Compile Results
    results = [res_placebo_mean, res_placebo_median, res_main_mean, res_main_median]
    res_df = pd.DataFrame(results)
    
    print("\n=========================================")
    print("      STACKED RDD ANALYSIS RESULTS       ")
    print("=========================================\n")
    print(res_df[["Label", "Estimate", "Std.Err", "P-value", "N"]].round(4).to_string(index=False))
    
    # 5. Visual Comparison — two-bar chart (Mean estimates only; log-points scale)
    mean_df = res_df[res_df["Label"].str.contains("Mean")].reset_index(drop=True)
    labels_plot = ["Placebo years\n(2018-2020)", "2021 cohort\n(LLM cutoff)"]
    estimates_plot = mean_df["Estimate"].values
    ses_plot = mean_df["Std.Err"].values
    colors_plot = ["#4C72B0", "#DD8452"]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = [0, 1]
    ax.bar(x, estimates_plot, width=0.5, color=colors_plot, alpha=0.85,
           yerr=ses_plot * 1.96, capsize=6, error_kw={"elinewidth": 1.5, "ecolor": "black"})

    for xi, est, se in zip(x, estimates_plot, ses_plot):
        ax.text(xi, est + se * 1.96 + 0.04, f"+{est:.1f}%",
                ha="center", va="bottom", fontsize=13, fontweight="bold")

    bracket_x = 1.22
    ax.annotate("", xy=(bracket_x, estimates_plot[1]), xytext=(bracket_x, estimates_plot[0]),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.8))
    ax.text(bracket_x + 0.06, (estimates_plot[0] + estimates_plot[1]) / 2,
            r"$\beta_3$" + "\n(LLM effect)", va="center", ha="left", fontsize=13)

    ax.set_xlim(-0.5, 1.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels_plot)
    ax.set_ylabel("Cutoff discontinuity (log points ≈ %)")
    ax.set_title("Diff-in-RDD intuition: subtract the placebo seasonal jump", pad=10)
    ax.set_ylim(0, max(estimates_plot) + max(ses_plot) * 1.96 + 0.35)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.text(0.5, -0.16,
            "52-week downloads, h = 26 illustrative spec.\n"
            r"Headline (post-AI window, h = 13): $\beta_3$ = $-$7%; see slide 11.",
            transform=ax.transAxes, ha="center", va="top", fontsize=10, color="#555555")

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    plt.savefig(FIG_ROBUSTNESS / "stacked_rdd_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    res_df.to_csv(RESULTS_ROBUSTNESS / "stacked_rdd_results.csv", index=False)
    print(f"\nSaved results to: {RESULTS_ROBUSTNESS / 'stacked_rdd_results.csv'}")

if __name__ == "__main__":
    main()
